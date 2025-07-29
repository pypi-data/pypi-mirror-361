import requests
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, root_validator
import json
from .entities import Entity
from .relationships import Relationship, MappedRelationship
from urllib.parse import urljoin
import sys

def build_raw_data(data: dict) -> dict:
    """
    Build a valid _rawData object with an 'autoParse' entry containing application/json content.
    """
    return {
        "autoParse": {
            "body": json.dumps(data),
            "contentType": "application/json"
        }
    }

def create_entity(_key: str, _type: str, _class: str = None, raw_data: dict = None, **kwargs) -> dict:
    data = {"_key": _key, "_type": _type}
    if _class is not None:
        data["_class"] = _class
    if raw_data is not None:
        data["_rawData"] = build_raw_data(raw_data)
    data.update(kwargs)
    return Entity(**data).model_dump(by_alias=True)

def create_relationship(_key: str, _type: str, _class: str, _fromEntityKey: str, _toEntityKey: str, **kwargs) -> dict:
    data = {
        "_key": _key,
        "_type": _type,
        "_class": _class,
        "_fromEntityKey": _fromEntityKey,
        "_toEntityKey": _toEntityKey,
    }
    data.update(kwargs)
    return Relationship(**data).model_dump(by_alias=True)

def create_mapped_relationship(_key: str, _type: str, _class: str, _mapping: dict = None, **kwargs) -> dict:
    data = {
        "_key": _key,
        "_type": _type,
        "_class": _class,
    }
    if _mapping is not None:
        data["_mapping"] = _mapping
    data.update(kwargs)
    return MappedRelationship(**data).model_dump(by_alias=True)

class JupiterOnePyoneer:
    def __init__(self, integration_instance_id: str, api_token: str, account: str, api_url: str = "https://api.us.jupiterone.io"):
        self.integration_instance_id = integration_instance_id
        self.api_token = api_token
        self.account = account
        self.api_url = urljoin(api_url.rstrip('/') + '/', 'persister/synchronization')
        self.sync_job_id: Optional[str] = None
        self.headers = {
            "Content-Type": "application/json",
            "Jupiterone-Account": self.account,
            "Authorization": f"Bearer {self.api_token}",
        }

    def create_sync_job(self, sync_mode: str = "DIFF") -> str:
        if sync_mode != "DIFF":
            raise ValueError("Only DIFF sync mode is supported")
        payload = {
            "source": "integration-external",
            "integrationInstanceId": self.integration_instance_id,
            "syncMode": sync_mode,
        }
        response = requests.post(f"{self.api_url}/jobs", json=payload, headers=self.headers)
        response.raise_for_status()
        sys.stderr.write(f"Started Sync Job: {response.json()['job']['id']}\n")
        self.sync_job_id = response.json()["job"]["id"]
        return self.sync_job_id

    def upload_entities(self, entities: List[Dict], batch_size: int = 100):
        if not self.sync_job_id:
            raise ValueError("Sync job not created. Call create_sync_job() first.")
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i+batch_size]
            payload = {"entities": batch}
            resp = requests.post(f"{self.api_url}/jobs/{self.sync_job_id}/entities", json=payload, headers=self.headers)
            sys.stderr.write(f"Uploaded {len(batch)} Entities (batch {i//batch_size+1}/{len(entities)//batch_size+1})\n")
            resp.raise_for_status()

    def upload_relationships(self, relationships: List[Dict], batch_size: int = 100):
        if not self.sync_job_id:
            raise ValueError("Sync job not created. Call create_sync_job() first.")
        for i in range(0, len(relationships), batch_size):
            batch = relationships[i:i+batch_size]
            payload = {"relationships": batch}
            resp = requests.post(f"{self.api_url}/jobs/{self.sync_job_id}/relationships", json=payload, headers=self.headers)
            sys.stderr.write(f"Uploaded {len(batch)} Relationships (batch {i//batch_size+1}/{len(relationships)//batch_size+1})\n")
            resp.raise_for_status()

    def finalize_sync_job(self):
        if not self.sync_job_id:
            raise ValueError("Sync job not created. Call create_sync_job() first.")
        resp = requests.post(f"{self.api_url}/jobs/{self.sync_job_id}/finalize", headers=self.headers)
        sys.stderr.write(f"Sync Job {resp.json()['job']['id']} Closed (status:{resp.json()['job']['status']})\n")
        sys.stderr.write(f" ├─ Uploaded {resp.json()['job']['numEntitiesUploaded']} Total Entities\n")
        sys.stderr.write(f" └─ Uploaded {resp.json()['job']['numRelationshipsUploaded']} Total Relationships\n")
        resp.raise_for_status() 
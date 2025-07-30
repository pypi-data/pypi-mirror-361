from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Any, Dict, Optional

class RelationshipDirection(str, Enum):
    FORWARD = "FORWARD"
    REVERSE = "REVERSE"

class Mapping(BaseModel):
    sourceEntityKey: str
    relationshipDirection: RelationshipDirection
    targetFilterKeys: List[List[str]]
    targetEntity: Optional[Dict[str, Any]] = None
    skipTargetCreation: bool = True

class Relationship(BaseModel):
    key: str = Field(..., alias="_key", description="Unique key for the relationship")
    type: str = Field(..., alias="_type", description="Type of the relationship")
    class_: str = Field(..., alias="_class", description="Class of the relationship (e.g., VERB)")
    from_entity_key: str = Field(..., alias="_fromEntityKey", description="Source entity key")
    to_entity_key: str = Field(..., alias="_toEntityKey", description="Target entity key")
    # Additional arbitrary fields allowed
    class Config:
        extra = "allow"
        validate_by_name = True 

class MappedRelationship(BaseModel):
    key: str = Field(..., alias="_key", description="Unique key for the relationship")
    type: str = Field(..., alias="_type", description="Type of the relationship")
    class_: str = Field(..., alias="_class", description="Class of the relationship (e.g., VERB)")
    mapping: Optional[Mapping] = Field(None, alias="_mapping", description="Mapping details for the relationship")
    # Additional arbitrary fields allowed
    class Config:
        extra = "allow"
        validate_by_name = True 

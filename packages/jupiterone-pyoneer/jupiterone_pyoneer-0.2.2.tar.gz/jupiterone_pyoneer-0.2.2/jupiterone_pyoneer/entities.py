from pydantic import BaseModel, Field
from typing import Union, List

class Entity(BaseModel):
    key: str = Field(..., alias="_key", description="Unique key for the entity")
    type: str = Field(..., alias="_type", description="Type of the entity")
    class_: Union[str, List[str]] = Field(None, alias="_class", description="Class of the entity (string or list of strings)")
    # Additional arbitrary fields allowed
    class Config:
        extra = "allow"
        validate_by_name = True 
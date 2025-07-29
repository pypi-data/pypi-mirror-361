from pydantic import BaseModel, Field

class Entity(BaseModel):
    key: str = Field(..., alias="_key", description="Unique key for the entity")
    type: str = Field(..., alias="_type", description="Type of the entity")
    class_: str = Field(None, alias="_class", description="Class of the entity")
    # Additional arbitrary fields allowed
    class Config:
        extra = "allow"
        validate_by_name = True 
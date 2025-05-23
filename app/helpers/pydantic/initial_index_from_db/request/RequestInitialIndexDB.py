from pydantic import BaseModel, Field

from app.helpers.Enums import CollectionTypesEnum


class RequestInitialIndexDb(BaseModel):
    batch: int = Field(100000, description="batch")
    skip: int = Field(0, description="skip")
    mul: bool = Field(True, description="mul")
    collection_type: CollectionTypesEnum = Field(..., description="collection type")

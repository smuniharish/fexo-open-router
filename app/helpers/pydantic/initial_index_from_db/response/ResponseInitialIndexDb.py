from pydantic import BaseModel, Field


class ResponseInitialIndexDb(BaseModel):
    status: str = Field(..., description="status of the response")

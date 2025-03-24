from pydantic import BaseModel, Field


class ResponseAddIndexDto(BaseModel):
    status: str = Field(..., description="status of the response")

from pydantic import BaseModel, Field
from typing import List

from pydantic import BaseModel, Field
from typing import List

class Tenant(BaseModel):
    id: str = Field(..., description="Tenant unique identifier")
    api_key: str = Field(..., description="API key for authentication")
    allowed_models: List[str] = Field(default_factory=list, description="List of models accessible to the tenant")
    allowed_providers: List[str] = Field(default_factory=list, description="List of providers allowed for the tenant")
    quota: int = Field(0, description="Quota limit for tenant requests")

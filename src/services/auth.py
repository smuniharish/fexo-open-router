from fastapi import Header, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import List,Optional
from src.helpers.utilities.custom.yaml_config import yamlConfig

class Tenant(BaseModel):
    id:str = Field(...,description="Id")
    api_key:str = Field(...,description="api_key")
    allowed_models:List[str] = []
    allowed_providers:List[str] = []
    quota:int = 0
    
def find_tenant_by_api_key(api_key:str)->Optional[Tenant]:
    """
    Lookup tenant by api_key from loaded tenants config.
    Return Tenant instance if found, else None.
    """
    tenants = yamlConfig.tenants or {}
    for tenant_key,tenant_data in tenants.items():
        if tenant_data.get("api_key") == api_key:
            allowed_models = tenant_data.get("allowed_models",[])
            allowed_providers_set = set()
            for model_name in allowed_models:
                model_info = None
                for series in yamlConfig.models_catalog.values():
                    for model in series.get("models",[]):
                        if model.get("name") == model_name:
                            model_info = model
                            break
                    if model_info:
                        break
                if model_info:
                    for provider in model_info.get("providers",[]):
                        allowed_providers_set.add(provider["name"])
    return Tenant(
        id = tenant_data.get("id",tenant_key),
        api_key = api_key,
        allowed_models = allowed_models,
        allowed_providers = list(allowed_providers_set),
        quota = tenant_data.get("quota",0)
    )

async def authenticate_tenant(authorization:str = Header(...,alias="Authorization"))-> Tenant:
    """
    FastAPI dependency to authenticate tenant by API key header.
    Raises 401 if invalid
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401,detail="Invalid Authorization header format")
    api_key = authorization[len("Bearer "):]
    tenant = find_tenant_by_api_key(api_key)
    if not tenant:
        raise HTTPException(status_code = 401,detail="Invalid API key")
    return tenant

async def validate_model_for_tenant(request:Request,tenant:Tenant = Depends(authenticate_tenant)):
    """
    FastAPI dependency to validate that requested model is allowed for tenant.
    Expects JSON body with a 'model' field.
    """
    body = await request.json()
    requested_model = body.get("model")
    if not requested_model:
        raise HTTPException(status_code=400,detail="Model field is required in the request body")
    if requested_model not in tenant.allowed_models:
        raise HTTPException(status_code=403,detail=f"Model '{requested_model}' not allowed for tenant")
    return tenant
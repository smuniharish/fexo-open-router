from typing import Optional

from fastapi import Depends, Header, HTTPException, Request

from src.helpers.models.pydantic.auth import Tenant
from src.helpers.utilities.custom.yaml_config import yamlConfig


def find_tenant_by_api_key(api_key: str) -> Optional[Tenant]:
    tenants = yamlConfig.tenants or {}
    for tenant_key, tenant_data in tenants.items():
        if tenant_data.get("api_key") == api_key:
            allowed_models = tenant_data.get("allowed_models", [])
            allowed_providers_set = set()
            for model_name in allowed_models:
                model_info = None
                for series in yamlConfig.models_catalog.values():
                    for model in series.get("models", []):
                        if model.get("name") == model_name:
                            model_info = model
                            break
                    if model_info:
                        break
                if model_info:
                    for provider in model_info.get("providers", []):
                        allowed_providers_set.add(provider["name"])
            return Tenant(
                id=tenant_data.get("id", tenant_key),
                api_key=api_key,
                allowed_models=allowed_models,
                allowed_providers=list(allowed_providers_set),
                quota=tenant_data.get("quota", 0),
            )
    return None


async def authenticate_tenant(authorization: str = Header(..., alias="Authorization")) -> Tenant:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    api_key = authorization[len("Bearer ") :].strip()
    tenant = find_tenant_by_api_key(api_key)
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return tenant


async def validate_model_for_tenant(request: Request, tenant: Tenant = Depends(authenticate_tenant)) -> Tenant:
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    requested_model = body.get("model")
    if not requested_model:
        raise HTTPException(status_code=400, detail="Model field is required in the request body")
    if requested_model not in tenant.allowed_models:
        raise HTTPException(status_code=403, detail=f"Model '{requested_model}' not allowed for tenant")
    return tenant

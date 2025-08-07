from typing import Any

from fastapi import APIRouter,Request,Depends
from fastapi.responses import ORJSONResponse

from src.services.auth import Tenant, validate_model_for_tenant
from src.services.route import ModelRouter

router = APIRouter(prefix="/v1/chat", tags=["chat"])

model_router = ModelRouter()
@router.post("/completions")
async def chat_completions(request:Request,tenant:Tenant = Depends(validate_model_for_tenant)) -> dict[Any, Any]:
    """
    Unified chat completions endpoint.
    Authenticates tenant, validates requested model,
    then routes to appropriate provider with failover.
    """
    try:
        payload = await request.json()
        model = payload.get("model")
        response = await model_router.route_request(
            tenant_id=tenant.id,
            model_name=model,
            payload=payload
        )
        return ORJSONResponse(content=response)
    except Exception as e:
        return ORJSONResponse(status_code=500,content={"error":str(e)})
    

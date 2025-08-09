
from fastapi import APIRouter, Depends, Request
from fastapi.responses import ORJSONResponse

from src.services.auth import Tenant, validate_model_for_tenant
from src.services.route import get_model_router

router = APIRouter(prefix="/v1/chat", tags=["chat"])


@router.post("/completions")
async def chat_completions(request: Request, tenant: Tenant = Depends(validate_model_for_tenant)) -> ORJSONResponse:
    """
    Unified chat completions endpoint.
    Authenticates tenant, validates requested model,
    then routes to appropriate provider with failover.
    """
    try:
        payload = await request.json()
        model = payload.get("model")
        model_router = get_model_router()
        response = await model_router.route_request(tenant_id=tenant.id, model_name=model, payload=payload)
        return ORJSONResponse(content=response)
    except Exception as e:
        return ORJSONResponse(status_code=500, content={"error": str(e)})

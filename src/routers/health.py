from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
def ping() -> dict[Any, Any]:
    return {"message": "server is up and running..."}

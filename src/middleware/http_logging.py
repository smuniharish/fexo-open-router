import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.monotonic()

        # Log the incoming request details
        logger.info(
            "Request start",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else None,
                "headers": dict(request.headers),
            },
        )

        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception before propagating
            logger.error(
                "Request processing error",
                exc_info=True,
                extra={"method": request.method, "url": str(request.url)},
            )
            raise

        process_time = time.monotonic() - start_time

        # Log the outgoing response details
        logger.info(
            "Request complete",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
            },
        )
        return response

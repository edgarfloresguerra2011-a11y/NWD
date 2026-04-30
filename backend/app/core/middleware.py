"""
Nexus Warmup Engine — Middleware
Request tracing, metrics collection, and error context enrichment.
"""
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from app.core.observability import metrics, TraceContext
import logging

logger = logging.getLogger("nexus.middleware")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Assigns a trace_id to every request
    2. Measures latency (p50, p95, p99)
    3. Records success/failure metrics
    4. Enriches error responses with trace context
    """
    
    async def dispatch(self, request: Request, call_next):
        trace = TraceContext()
        trace.set_attribute("method", request.method)
        trace.set_attribute("path", request.url.path)
        
        # Inject trace_id into request state for downstream use
        request.state.trace_id = trace.trace_id
        
        try:
            response = await call_next(request)
            
            duration = trace.duration_ms
            success = response.status_code < 500
            metrics.record_request(duration, success)
            
            # Attach trace headers to response
            response.headers["X-Trace-ID"] = trace.trace_id
            response.headers["X-Duration-Ms"] = str(round(duration, 2))
            
            # Log slow requests (> 2 seconds)
            if duration > 2000:
                logger.warning(
                    f"Slow request: {request.method} {request.url.path} took {duration:.0f}ms",
                    extra={"trace_id": trace.trace_id, "duration_ms": duration}
                )
            
            return response
            
        except Exception as exc:
            duration = trace.duration_ms
            metrics.record_request(duration, success=False)
            
            logger.error(
                f"Unhandled error: {request.method} {request.url.path} — {exc}",
                exc_info=True,
                extra={
                    "trace_id": trace.trace_id,
                    "duration_ms": duration,
                    "extra_data": {
                        "method": request.method,
                        "path": request.url.path,
                        "client": request.client.host if request.client else "unknown",
                    }
                }
            )
            
            # Return error with trace_id so user can report it
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "trace_id": trace.trace_id,
                    "message": "Report this trace_id for investigation.",
                },
                headers={"X-Trace-ID": trace.trace_id}
            )

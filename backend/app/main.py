from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.core.observability import setup_structured_logging
from app.core.middleware import ObservabilityMiddleware
from app.api import auth, accounts, campaigns, analytics, warmup, domains
from app.api import billing, health
from app.core.rate_limit import limiter, _rate_limit_exceeded_handler, RateLimitExceeded
from fastapi.middleware.trustedhost import TrustedHostMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    setup_structured_logging()
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Email Warming & Cold Email Platform API",
    lifespan=lifespan,
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security: Prevent host header attacks
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*.nexusengine.com"]
)

# Observability middleware (must be added before CORS)
app.add_middleware(ObservabilityMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://*.nexusengine.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(campaigns.router)
app.include_router(analytics.router)
app.include_router(warmup.router)
app.include_router(domains.router)
app.include_router(billing.router)
app.include_router(health.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "env": settings.ENVIRONMENT}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

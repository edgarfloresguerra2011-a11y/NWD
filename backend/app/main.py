"""
Nexus Engine — FastAPI Application
Email Warming & Cold Email Platform
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api import auth, accounts, campaigns, analytics, warmup, domains


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Email Warming & Cold Email Platform API",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://*.nexusengine.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION, "app": settings.APP_NAME}

# Mount routers
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(campaigns.router)
app.include_router(analytics.router)
app.include_router(warmup.router)
app.include_router(domains.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

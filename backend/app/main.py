from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, accounts, campaigns
from app.core.config import settings
from app.db.session import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas al arrancar (en producción usar Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Nexus Warmup Dashboard",
    description="API para gestión de warmup de emails y campañas cold email",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — en producción reemplazar "*" por el dominio real del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(accounts.router, prefix="/api/v1")
app.include_router(campaigns.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.environment}

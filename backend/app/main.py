import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.database import Base, engine
from app import models  # noqa: F401 -- ensures all models are registered before create_all

from app.api.routes import auth, vehicles, riders, deliveries, maintenance, alerts, dashboard, chat, reports, admin, ml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ev_fleet")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")
    if not settings.has_llm_key:
        logger.warning(
            "No LLM API key configured for provider '%s'. AI Chat will run in "
            "data-only fallback mode until a key is added to .env.",
            settings.LLM_PROVIDER,
        )
    yield


app = FastAPI(
    title="EV Fleet Intelligence Multi-Agent System",
    description="AI-powered fleet intelligence platform for EV logistics operations.",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url)
    return JSONResponse(status_code=500, content={"detail": "An unexpected error occurred. Please try again."})


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_key_configured": settings.has_llm_key,
    }


app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(riders.router)
app.include_router(deliveries.router)
app.include_router(maintenance.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
app.include_router(chat.router)
app.include_router(reports.router)
app.include_router(admin.router)
app.include_router(ml.router)

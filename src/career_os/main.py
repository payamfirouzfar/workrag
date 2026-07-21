from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import get_settings
from .core.logging import configure_logging, get_logger

SETTINGS = get_settings()
configure_logging(SETTINGS.app_env)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("career_os_starting", env=SETTINGS.app_env)
    yield
    logger.info("career_os_shutdown")


app = FastAPI(title="AI Career OS", version="0.1.0", lifespan=lifespan)


def _include_routers() -> None:
    # Imported lazily so a missing optional dependency doesn't break
    # `python -m career_os.agents.orchestrator worker`, which never touches
    # the API layer.
    from .api.routes_profile import router as profile_router
    from .api.routes_jobs import router as jobs_router
    from .api.routes_applications import router as applications_router
    from .api.routes_email import router as email_router
    from .api.routes_approval import router as approval_router

    app.include_router(profile_router)
    app.include_router(jobs_router)
    app.include_router(applications_router)
    app.include_router(email_router)
    app.include_router(approval_router)


_include_routers()


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok"}

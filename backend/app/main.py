import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.data.scheduler import run_background_refresh_loop
from app.data.refresh import bootstrap_application, refresh_application_data


settings = get_settings()
logger = logging.getLogger(__name__)


async def run_startup_refresh() -> None:
    try:
        await asyncio.to_thread(refresh_application_data, settings)
    except Exception:
        logger.exception("Startup refresh failed.")


@asynccontextmanager
async def lifespan(_: FastAPI):
    should_run_startup_refresh = await asyncio.to_thread(bootstrap_application)
    startup_refresh_task: asyncio.Task[None] | None = None
    refresh_task: asyncio.Task[None] | None = None
    if should_run_startup_refresh:
        startup_refresh_task = asyncio.create_task(run_startup_refresh())
    if settings.background_refresh_enabled:
        refresh_task = asyncio.create_task(run_background_refresh_loop(settings=settings))
    try:
        yield
    finally:
        if startup_refresh_task is not None:
            startup_refresh_task.cancel()
            with suppress(asyncio.CancelledError):
                await startup_refresh_task
        if refresh_task is not None:
            refresh_task.cancel()
            with suppress(asyncio.CancelledError):
                await refresh_task


app = FastAPI(title=settings.app_name, lifespan=lifespan)

allowed_origins = {
    settings.frontend_origin,
    "http://frontend:3000",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(allowed_origins),
    allow_origin_regex=settings.frontend_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "SignalStack API", "status": "online"}

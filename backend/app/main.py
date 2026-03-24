import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.data.scheduler import run_background_refresh_loop
from app.data.refresh import bootstrap_application


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    bootstrap_application()
    refresh_task: asyncio.Task[None] | None = None
    if settings.background_refresh_enabled:
        refresh_task = asyncio.create_task(run_background_refresh_loop(settings=settings))
    try:
        yield
    finally:
        if refresh_task is not None:
            refresh_task.cancel()
            with suppress(asyncio.CancelledError):
                await refresh_task


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://frontend:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "SignalStack API", "status": "online"}

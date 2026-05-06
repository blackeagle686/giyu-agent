"""
Giyu Backend — FastAPI application factory.
"""
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .state import log, get_agent, set_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.warning(f"🔥 Giyu Server starting in {os.getcwd()} …")
    asyncio.create_task(_initialize_agent())
    yield
    log.warning("🛑 Giyu Agent server shut down.")


async def _initialize_agent():
    try:
        from giyu.agent import get_giyu_agent
        log.warning("🧠 Loading AI modules & Phoenix framework…")
        agent = await get_giyu_agent()
        set_agent(agent)
        log.warning("✅ Giyu Agent is now READY.")
    except Exception as exc:
        log.error(f"❌ Failed to initialize agent: {exc}", exc_info=True)


def create_app() -> FastAPI:
    """Build and return a fully configured FastAPI application."""
    application = FastAPI(
        title="Giyu Agent API",
        version="1.0.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check (inline — too small for its own file)
    @application.get("/health")
    async def health():
        return {"status": "ok", "agent_ready": get_agent() is not None}

    # Register route modules
    from .routes_chat import router as chat_router
    from .routes_code import router as code_router
    from .routes_config import router as config_router
    from .routes_media import router as media_router
    from .routes_stability import router as stability_router
    from fastapi.staticfiles import StaticFiles

    application.include_router(chat_router)
    application.include_router(code_router)
    application.include_router(config_router)
    application.include_router(media_router)
    application.include_router(stability_router)

    # Mount Dashboard
    dashboard_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "dashboard")
    if os.path.exists(dashboard_path):
        application.mount("/dashboard", StaticFiles(directory=dashboard_path, html=True), name="dashboard")

    return application


# Module-level app instance (used by uvicorn)
app = create_app()

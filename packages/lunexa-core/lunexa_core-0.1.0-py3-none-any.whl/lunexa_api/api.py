"""API logic for Lunexa API plugin."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Runtime configuration loaded from env vars or `.env`."""

    model_path: str = "model.onnx"


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: D401
    """Lazy-load heavy resources on startup, close them on shutdown."""
    # e.g. model = load_model(settings.model_path)
    yield
    # model.unload()  # if needed


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(title="Lunexa API", lifespan=lifespan)

    @app.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        """Liveness probe for Kubernetes/Helm."""
        return {"status": "ok"}

    return app


# Global app instance
app = create_app()

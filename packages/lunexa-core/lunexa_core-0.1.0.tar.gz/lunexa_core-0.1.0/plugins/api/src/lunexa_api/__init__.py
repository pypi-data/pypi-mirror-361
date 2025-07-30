"""Lunexa API plugin."""

import typer
import uvicorn

from .api import app

# ─── Typer CLI plug-in ──────────────
cli = typer.Typer(help="Serve the FastAPI app")


@cli.command()
def serve(host: str = "127.0.0.1", port: int = 8000) -> None:  # nosec B104
    """Run the API with Uvicorn (reload=True for dev)."""
    uvicorn.run("lunexa_api:app", host=host, port=port, reload=True)

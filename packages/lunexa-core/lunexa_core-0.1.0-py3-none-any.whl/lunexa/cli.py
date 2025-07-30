from __future__ import annotations

import importlib.metadata
import sys

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Lunexa Core - Umbrella CLI for all Lunexa projects",
)


def _load_plugins() -> None:
    """Discover and load plugins."""
    if sys.version_info >= (3, 10):
        # Python 3.10+ supports the group argument
        entry_points = importlib.metadata.entry_points(group="lunexa.plugins")
    else:
        # Python 3.9 and older: entry_points() returns a dict
        all_entry_points = importlib.metadata.entry_points()
        entry_points = all_entry_points.get("lunexa.plugins", [])
    for ep in entry_points:
        app.add_typer(ep.load(), name=ep.name)


@app.command()
def version() -> None:
    """Print the currently installed package version."""
    pkg_version = importlib.metadata.version("lunexa-core")
    console.print(Panel(f"lunexa-core {pkg_version}", title="Version"))


@app.command()
def info() -> None:
    """Show project information."""
    console.print(
        Panel(
            "[bold blue]Lunexa Core[/bold blue]\n"
            "Umbrella CLI & shared utils for all Lunexa projects\n\n"
            "[yellow]Available plugins:[/yellow]\n"
            "- api: FastAPI scaffold",
            title="Project Info",
        )
    )


_load_plugins()


def main() -> None:
    """CLI entry-point."""
    app()


if __name__ == "__main__":
    main()

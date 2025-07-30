"""Core utility functions for Lunexa."""

import importlib.metadata


def get_project_info() -> dict[str, object]:
    """Get project information."""
    try:
        version = importlib.metadata.version("lunexa-core")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"
    return {
        "name": "lunexa-core",
        "version": version,
        "description": "Umbrella CLI & shared utils for all Lunexa projects",
        "plugins": ["api"],
    }


def validate_config(config: dict[str, object]) -> bool:
    """Validate configuration dictionary."""
    required_keys = ["name", "version"]
    return all(key in config for key in required_keys)

# asr/plugin.py
import pluggy

from .models import ModelRegistry

hookspec = pluggy.HookspecMarker("mstt")
"""Hook specification marker for `mstt` plugins."""
hookimpl = pluggy.HookimplMarker("mstt")
"""Hook implementation marker for `mstt` plugins."""


@hookspec
def register_models(registry: ModelRegistry):
    """
    A hook for plugins to register their ASR models with the main application.

    Plugins implementing this hook should add their `AsrModel` subclasses
    to the provided `registry`.

    Args:
        registry (ModelRegistry): The central model registry to which models should be added.
    """

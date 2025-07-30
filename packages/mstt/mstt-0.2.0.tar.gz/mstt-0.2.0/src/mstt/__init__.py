import pluggy

from . import plugin
from .models import AsrModel, ModelRegistry

# Global model registry and plugin manager instances.
_model_registry: ModelRegistry | None = None
_pm: pluggy.PluginManager | None = None


def get_plugin_manager() -> pluggy.PluginManager:
    """
    Retrieves or initializes the global Pluggy plugin manager.

    The plugin manager is responsible for discovering and managing
    plugins that extend `mstt`'s functionality, particularly for
    registering ASR models.

    Returns:
        pluggy.PluginManager: The initialized plugin manager instance.
    """
    global _pm
    if _pm is None:
        _pm = pluggy.PluginManager("mstt")
        _pm.add_hookspecs(plugin)
        _pm.load_setuptools_entrypoints("mstt")
    return _pm


def get_model_registry() -> ModelRegistry:
    """
    Retrieves or initializes the global ASR model registry.

    The model registry stores and manages available ASR models,
    including those registered via plugins.

    Returns:
        ModelRegistry: The initialized model registry instance.
    """
    global _model_registry
    if _model_registry is None:
        _model_registry = ModelRegistry()
        get_plugin_manager().hook.register_models(registry=_model_registry)
    return _model_registry


def get_model(model_id: str) -> AsrModel:
    """
    Get an instance of an ASR model.

    This function first checks for models registered by plugins.
    If not found, it checks if the model_id looks like a Hugging Face
    Hub identifier (e.g., "openai/whisper-tiny") and, if so, attempts
    to load it dynamically using the transformers library.
    """
    registry = get_model_registry()

    # 1. Check for explicitly registered models from plugins
    model_class = registry.get_class(model_id)
    if model_class:
        return model_class(model_id)

    # 2. Check for prefix matches (new feature!)
    # e.g., model_id="funasr/iic/SenseVoiceSmall" should match a handler for "funasr/"
    for prefix, handler_class in registry.models.items():
        if model_id.startswith(prefix):
            # Ensure this is a wildcard registration, e.g., prefix is 'funasr/'
            if prefix.endswith("/"):
                return handler_class(model_id)

    # 3. If not found, try to treat it as a dynamic Hugging Face model
    if "/" in model_id and not any(
        model_id.startswith(p) for p in registry.models.keys() if p.endswith("/")
    ):
        try:
            # Dynamically import and use the generic TransformersModel
            from .models import TransformersModel

            return TransformersModel(model_id=model_id)
        except ImportError:
            # This happens if transformers is not installed
            raise ImportError(
                f"To use Hugging Face model '{model_id}', "
                "you need to install the [transformers] extra:\n\n"
                "  pip install mstt[transformers]"
            ) from None
        except Exception as e:
            # This can happen if the model_id is invalid on the Hub
            raise KeyError(
                f"Failed to load Hugging Face model '{model_id}'. "
                f"Please ensure it's a valid ASR model on the Hub. Original error: {e}"
            ) from e

    # 3. If all else fails, raise an error
    available = list(registry.models.keys())
    raise KeyError(
        f"Model '{model_id}' not found. "
        f"Available registered models: {available}. "
        "Or, provide a valid Hugging Face model ID (e.g., 'openai/whisper-base')."
    )


def models() -> list[str]:
    """
    Returns a list of available model IDs.

    Returns:
        list[str]: A list of strings, where each string is a model ID.
    """
    return list(get_model_registry().models.keys())

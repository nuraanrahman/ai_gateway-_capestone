from app.providers.base import ChatProvider
from app.providers.openai_provider import OpenAIProvider
from app.providers.anthropic_provider import AnthropicProvider

# Model prefix → provider name
MODEL_PROVIDER_MAP: dict[str, str] = {
    "gpt": "openai",
    "o1": "openai",
    "o3": "openai",
    "claude": "anthropic",
}

# Singleton instances
_registry: dict[str, ChatProvider] = {
    "openai": OpenAIProvider(),
    "anthropic": AnthropicProvider(),
}


def get_provider(model: str) -> ChatProvider:
    """Resolve a model string to its provider instance."""
    for prefix, provider_name in MODEL_PROVIDER_MAP.items():
        if model.lower().startswith(prefix):
            provider = _registry[provider_name]
            if not provider.is_configured:
                raise ValueError(f"{provider_name}_not_configured")
            return provider
    raise ValueError(f"unknown_model: {model!r}")


def list_providers() -> list[dict]:
    return [
        {"name": p.name, "status": "configured" if p.is_configured else "not_configured"}
        for p in _registry.values()
    ]

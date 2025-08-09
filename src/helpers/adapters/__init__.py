from typing import Any, Dict

from src.helpers.adapters.anthropic import AnthropicAdapter
from src.helpers.adapters.base import BaseProviderAdapter
from src.helpers.adapters.google import GoogleGeminiAdapter
from src.helpers.adapters.openai import OpenAIAdapter
from src.helpers.utilities.custom.env_var import envConfig

internal_keys = {"openai": envConfig.openai_secret_key, "azure_openai": envConfig.azure_openai_secret_key, "anthropic": envConfig.anthropic_secret_key, "google": envConfig.google_secret_key, "xyzcloud": envConfig.xyzcloud_secret_key, "partnerai": envConfig.partnerai_secret_key}

adapter_classes = {
    "openai": OpenAIAdapter,
    "azure_openai": OpenAIAdapter,
    "anthropic": AnthropicAdapter,
    "google": GoogleGeminiAdapter,
    "xyzcloud": OpenAIAdapter,
    "partnerai": OpenAIAdapter,
}


def get_provider_adapter(provider_name: str, provider_config: Dict[str, Any]) -> BaseProviderAdapter:
    provider_config = provider_config.copy()
    provider_config["api_key_internal"] = internal_keys.get(provider_name)
    adapter_class = adapter_classes.get(provider_name)
    if not adapter_class:
        raise ValueError(f"No adapter found for provider:{provider_name}")
    return adapter_class(provider_config)

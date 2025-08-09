from typing import Any, Dict

import httpx

from src.helpers.adapters.base import BaseProviderAdapter


class AnthropicAdapter(BaseProviderAdapter):
    async def send_request(self, model_name: str, payload: Dict[str, Any]):
        url = f"{self.base_url}/chat/completions"
        headers = self.get_headers()

        data = {"model": model_name, "prompt": payload.get("prompt", ""), "max_tokens_to_sample": payload.get("max_tokens", 100), **payload}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()

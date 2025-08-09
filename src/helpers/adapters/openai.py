import random
import time
from typing import Any, Dict

import httpx

from src.helpers.adapters.base import BaseProviderAdapter


class OpenAIAdapter(BaseProviderAdapter):
    async def send_request(self, model_name: str, payload: Dict[str, Any]):
        url = f"{self.base_url}/chat/completions"
        headers = self.get_headers()

        data = {"model": model_name, **payload}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()

    async def send_request(self, model_name: str, payload: Dict[str, Any]):
        # url = f"{self.base_url}/chat/completions"
        # headers = self.get_headers()

        # data = {
        #     "model":model_name,
        #     **payload
        # }

        # async with httpx.AsyncClient() as client:
        #     response = await client.post(url,headers=headers,json=data)
        #     response.raise_for_status()
        #     return response.json()
        created_ts = int(time.time())
        return {"id": f"chatcmpl-mock-{random.randint(1000, 9999)}", "object": "chat.completion", "created": created_ts, "model": model_name, "choices": [{"index": 0, "message": {"role": "assistant", "content": f"Hello! This is a mocked response from {model_name}."}, "finish_reason": "stop"}], "usage": {"prompt_tokens": len(str(payload)), "completion_tokens": 10, "total_tokens": len(str(payload)) + 10}, "mock": True}

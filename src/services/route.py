import logging
from typing import Dict, List, Optional

from fastapi import HTTPException

from src.helpers.adapters import get_provider_adapter
from src.helpers.utilities.custom.yaml_config import yamlConfig

logger = logging.getLogger(__name__)


# --------------------------
# Routing Policy Engine
# --------------------------
class RoutingPolicyEngine:
    def __init__(self, routing_policies: Dict, models_catalog: Dict):
        self.policies = routing_policies or {}
        self.models_catalog = models_catalog or {}

    def get_series_by_model_name(self, model_name: str) -> Optional[str]:
        """
        Given a model name (e.g. gpt-3.5-turbo),
        find which series it belongs to in models_catalog (e.g. gpt).
        """
        for series_name, series_info in self.models_catalog.items():
            for model in series_info.get("models", []):
                if model.get("name") == model_name:
                    return series_name
        return None

    def get_tenant_policy(self, tenant_id: str, model_name: str) -> Dict:
        """
        Get routing policy for a given tenant+model series:
          1. Tenant-specific policy for that series
          2. Global/shared policy for that series
          3. Global default policy
        """
        series_name = self.get_series_by_model_name(model_name)
        if not series_name:
            return {}  # unknown model

        # 1️⃣ Tenant-specific policy for that series
        tenant_policy = self.policies.get(tenant_id, {})
        if series_name in tenant_policy:
            return tenant_policy[series_name]

        # 2️⃣ Global/shared policy for that series
        if series_name in self.policies:
            return self.policies[series_name]

        # 3️⃣ Fallback to generic global section
        return self.policies.get("global", {})

    def get_failover_providers(self, tenant_id: str, model_name: str, failed_provider: str) -> List[str]:
        """
        Return failover providers for the tenant/model's series, excluding the failed provider.
        """
        policy = self.get_tenant_policy(tenant_id, model_name)
        failover_order = policy.get("failover_order", [])
        return [p for p in failover_order if p != failed_provider]


# --------------------------
# Model Router
# --------------------------
class ModelRouter:
    def __init__(self):
        self.models_catalog = yamlConfig.models_catalog
        self.routing_engine = RoutingPolicyEngine(yamlConfig.routing_policies, self.models_catalog)

    def get_model_providers(self, model_name: str) -> List[str]:
        for series in self.models_catalog.values():
            for model in series.get("models", []):
                if model.get("name") == model_name:
                    return [provider["name"] for provider in model.get("providers", [])]
        return []

    @staticmethod
    def get_provider_health(provider_name: str) -> bool:
        return True  # stub

    @staticmethod
    def get_provider_latency(provider_name: str) -> float:
        simulated_latencies = {"openai": 120, "azure_openai": 140, "anthropic": 180, "google": 100, "xyzcloud": 160, "partnerai": 130}
        return simulated_latencies.get(provider_name, 100)

    @staticmethod
    def get_provider_cost(model_name: str, provider_info: dict) -> float:
        prompt_pricing = provider_info.get("prompt_pricing", {})
        return prompt_pricing.get("text", float("inf"))

    def get_provider_info(self, model_name: str, provider_name: str) -> Optional[Dict]:
        for series in self.models_catalog.values():
            for model in series.get("models", []):
                if model.get("name") == model_name:
                    for provider in model.get("providers", []):
                        if provider["name"] == provider_name:
                            return provider
        return None

    def select_primary_provider(self, tenant_id: str, model_name: str) -> Optional[str]:
        policy = self.routing_engine.get_tenant_policy(tenant_id, model_name)
        candidate_providers = policy.get("primary_providers", [])
        provider_scores = []

        for provider_name in candidate_providers:
            provider_info = self.get_provider_info(model_name, provider_name)
            if not provider_info or not self.get_provider_health(provider_name):
                continue
            latency = self.get_provider_latency(provider_name)
            cost = self.get_provider_cost(model_name, provider_info)
            score = latency + cost * 10000  # weight cost heavily
            provider_scores.append((provider_name, score))

        if not provider_scores:
            return None

        provider_scores.sort(key=lambda x: x[1])
        return provider_scores[0][0]

    async def route_request(self, tenant_id: str, model_name: str, payload: dict) -> dict:
        logging.info("Route request", extra={"tenant_id": tenant_id, "model_name": model_name})
        primary_provider = self.select_primary_provider(tenant_id, model_name)

        if not primary_provider:
            logging.error("Route Request Failed", exc_info=True, extra={"tenant_id": tenant_id, "model_name": model_name, "payload": payload})
            raise HTTPException(status_code=503, detail="No primary provider configured")

        providers_to_try = [primary_provider] + self.routing_engine.get_failover_providers(tenant_id, model_name, primary_provider)

        last_exception = None
        for provider_name in providers_to_try:
            provider_info = self.get_provider_info(model_name, provider_name)
            if not provider_info:
                continue
            adapter = get_provider_adapter(provider_name, provider_info)
            try:
                response = await adapter.send_request(model_name, payload)
                return response
            except Exception as e:
                last_exception = e

        raise HTTPException(status_code=502, detail=f"All providers failed: {str(last_exception)}")


# --------------------------
# Model Router Singleton
# --------------------------
model_router: Optional[ModelRouter] = None


def initializing_model_router():
    global model_router
    if model_router:
        return model_router
    model_router = ModelRouter()
    return model_router


def get_model_router():
    global model_router
    if not model_router:
        model_router = ModelRouter()
    return model_router

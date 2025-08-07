from typing import Dict, Optional, List
from fastapi import HTTPException
from src.helpers.adapters import get_provider_adapter
from src.helpers.utilities.custom.yaml_config import yamlConfig

class RoutingPolicyEngine:
    def __init__(self, routing_policies: Dict):
        self.policies = routing_policies or {}

    def get_tenant_policy(self, tenant_id: str) -> Dict:
        """
        Get routing policy for a tenant if exists, else fallback to global policy.
        """
        return self.policies.get(tenant_id) or self.policies.get("global") or {}

    def get_failover_providers(self, tenant_id: str, failed_provider: str) -> List[str]:
        """
        Return a list of failover providers, excluding the failed_provider.
        """
        policy = self.get_tenant_policy(tenant_id)
        failover_order = policy.get("failover_order", [])
        return [p for p in failover_order if p != failed_provider]

class ModelRouter:
    def __init__(self):
        self.models_catalog = yamlConfig.models_catalog
        self.routing_engine = RoutingPolicyEngine(yamlConfig.routing_policies)

    def get_model_providers(self, model_name: str) -> List[str]:
        """
        Retrieve list of providers that support the given model
        """
        for series in self.models_catalog.values():
            for model in series.get("models", []):
                if model.get("name") == model_name:
                    return [provider["name"] for provider in model.get("providers", [])]
        return []

    @staticmethod
    def get_provider_health(provider_name: str) -> bool:
        """Check provider health (stub for now)."""
        return True

    @staticmethod
    def get_provider_latency(provider_name: str) -> float:
        """Return provider latency (stub for now)."""
        simulated_latencies = {
            "openai": 120,
            "azure_openai": 140,
            "anthropic": 180,
            "google": 100,
            "xyzcloud": 160,
            "partnerai": 130
        }
        return simulated_latencies.get(provider_name, 100)

    @staticmethod
    def get_provider_cost(model_name: str, provider_info: dict) -> float:
        """Return provider cost (stub for now)."""
        prompt_pricing = provider_info.get("prompt_pricing", {})
        return prompt_pricing.get("text", float('inf'))

    def get_provider_info(self, model_name: str, provider_name: str) -> Optional[Dict]:
        """
        Get provider configuration for a given model and provider.
        """
        for series in self.models_catalog.values():
            for model in series.get("models", []):
                if model.get("name") == model_name:
                    for provider in model.get("providers", []):
                        if provider["name"] == provider_name:
                            return provider
        return None

    def select_primary_provider(self, tenant_id: str, model_name: str) -> Optional[str]:
        """
        Select primary provider for the tenant + model, considering health, latency and cost.
        """
        policy = self.routing_engine.get_tenant_policy(tenant_id)
        candidate_providers = policy.get("primary_providers", [])
        provider_scores = []
        for provider_name in candidate_providers:
            provider_info = self.get_provider_info(model_name, provider_name)
            if not provider_info:
                continue
            healthy = self.get_provider_health(provider_name)
            if not healthy:
                continue
            latency = self.get_provider_latency(provider_name)
            cost = self.get_provider_cost(model_name, provider_info)
            score = latency + cost * 10000
            provider_scores.append((provider_name, score))
        if not provider_scores:
            return None
        provider_scores.sort(key=lambda x: x[1])
        return provider_scores[0][0]

    async def route_request(self, tenant_id: str, model_name: str, payload: dict) -> dict:
        """
        Routes the request to appropriate provider with failover.
        Raises HTTPException on failure.
        """
        primary_provider = self.select_primary_provider(tenant_id, model_name)
        if not primary_provider:
            raise HTTPException(status_code=503, detail="No primary provider configured")

        providers_to_try = [primary_provider] + self.routing_engine.get_failover_providers(tenant_id, primary_provider)
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

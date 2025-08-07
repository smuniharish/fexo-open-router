from typing import Dict, Any

class BaseProviderAdapter:
    def __init__(self,provider_config:Dict[str,Any]):
        """
        Base adapter initialized with provider config from models_catalog.
        provider_config includes all details.
        """
        self.base_url = provider_config.get("base_url")
        self.api_key = provider_config.get("api_key_internal")
        
        if not self.api_key:
            raise ValueError("Provider API Key (internal) must be provided in config under 'api_key_internal'")
    async def send_request(self,model_name:str,payload:Dict[str,Any]) -> Dict[str,Any]:
        """
        Send the formatted request to the underlying model provider and return the parsed response. Must be overridden by subclasses.
        """
        raise NotImplementedError("send_request must be implemented in subclass")
    
    def get_headers(self) -> Dict[str,str]:
        return {
            "Authorization":f"Bearer {self.api_key}",
            "Content-Type":"application/json"
        }
        
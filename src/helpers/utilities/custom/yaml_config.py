import os

from src.helpers.utilities.generic.yaml_loader import load_yaml_config

CONFIG_DIR = "config"


class YAMLConfig:
    """
    Singleton container for loaded YAML configurations.
    """

    tenants = {}
    routing_policies = {}
    models_catalog = {}


yamlConfig = YAMLConfig()


def get_path(file_name: str) -> str:
    """
    Get full file path for a config file within CONFIG_DIR.
    """
    return os.path.join(CONFIG_DIR, file_name)


def load_yaml_configs():
    """
    Load all required YAML config files into the YAMLConfig singleton.
    Raises RuntimeError on failure with appropriate message.
    """
    try:
        models_catalog_path = get_path("models_catalog.yaml")
        tenants_path = get_path("tenants.yaml")
        routing_path = get_path("routing_policies.yaml")
        yamlConfig.models_catalog = load_yaml_config(models_catalog_path)
        yamlConfig.tenants = load_yaml_config(tenants_path)
        yamlConfig.routing_policies = load_yaml_config(routing_path)
    except FileNotFoundError as e:
        raise RuntimeError(f"Config file not found: {e.filename}")
    except Exception as e:
        raise RuntimeError(f"Error loading YAML config: {str(e)}")

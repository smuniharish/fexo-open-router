import yaml
from typing import Any, Dict

def load_yaml_config(file_path:str) -> Dict[str,Any]:
    """
    Helper to load a YAML configuration file into a dictionary.
    
    Args:
        file_path (str): Path to the YAML file.
    Returns:
        Dict[str,Any]:Parsed YAML content as a dictionary.
    """
    try:
        with open(file_path,'r',encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"YAML configuration file not found: {file_path}")
    except yaml.YAMLError as e:
        raise RuntimeError(f"Error parsing YAML file {file_path}: {e}")
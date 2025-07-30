"""
Centralized Configuration Management for the DPI System.

This module provides a ConfigManager to load and serve all system configurations
from a central directory.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import copy


def deep_merge_dicts(base: dict, override: dict) -> dict:
    """Recursively merge two dicts, with override taking precedence."""
    result = copy.deepcopy(base)
    for k, v in override.items():
        if (
            k in result
            and isinstance(result[k], dict)
            and isinstance(v, dict)
        ):
            result[k] = deep_merge_dicts(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result

class ConfigManager:
    """
    Centralized configuration manager for the DPI system.
    Loads system config as defaults, and merges user config as overrides.
    """
    def __init__(self, user_config_dir: str = "configs", system_config_dir: str = "src/system_config"):
        self.user_config_dir = Path(user_config_dir)
        self.system_config_dir = Path(system_config_dir)
        self._configs: Dict[str, Any] = {}
        self.load_all_configs()

    def load_all_configs(self) -> None:
        """
        Load all YAML configuration files from system config, then override with user config if present.
        """
        system_configs = self._load_configs_from_dir(self.system_config_dir)
        user_configs = self._load_configs_from_dir(self.user_config_dir)
        self._configs = deep_merge_dicts(system_configs, user_configs)
        if not self._configs:
            print(f"Warning: No configurations loaded from {self.system_config_dir} or {self.user_config_dir}")

    def _load_configs_from_dir(self, config_dir: Path) -> Dict[str, Any]:
        configs = {}
        if not config_dir.is_dir():
            return configs
        for config_file in config_dir.glob('*.yaml'):
            try:
                with open(config_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    configs = deep_merge_dicts(configs, data)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {config_file}: {e}")
            except Exception as e:
                print(f"Error loading config file {config_file}: {e}")
        # Also support JSON (for signatures)
        for config_file in config_dir.glob('*.json'):
            try:
                import json
                with open(config_file, 'r') as f:
                    data = json.load(f) or {}
                    configs = deep_merge_dicts(configs, data)
            except Exception as e:
                print(f"Error loading JSON config file {config_file}: {e}")
        return configs

    def get_config(self, key: str, default: Optional[Any] = None) -> Any:
        return self._configs.get(key, default)

    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        if 'dpi_engine' in self._configs and 'modules' in self._configs['dpi_engine']:
            if module_name in self._configs['dpi_engine']['modules']:
                return self._configs['dpi_engine']['modules'][module_name]
        if module_name in self._configs:
            return self._configs[module_name]
        return {}

    def get_logging_config(self) -> Dict[str, Any]:
        return self.get_config('logging', {})
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from .config import Config
from .config_validator import ConfigValidator
from .exceptions import ConfigurationError

class ConfigManager:
    """Advanced configuration management with environment support"""
    
    def __init__(self):
        self.config_dir = Config.get_app_data_dir()
        self.config_file = self.config_dir / 'config.yaml'
        self.env_dir = self.config_dir / 'environments'
        self._config_cache = None
        self._ensure_config_structure()
    
    def _ensure_config_structure(self):
        """Create configuration directory structure"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.env_dir.mkdir(exist_ok=True)
        
        # Create default config if not exists
        if not self.config_file.exists():
            self._create_default_config()
        
        # Create environment configs
        self._create_environment_configs()
    
    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            'version': '1.0',
            'environment': 'production',
            'logging': {
                'level': 'INFO',
                'file_enabled': True,
                'console_enabled': True
            },
            'optimization': {
                'default_pattern': 'adaptive_generation',
                'cache_enabled': True,
                'cache_ttl': 3600
            },
            'ui': {
                'progress_enabled': True,
                'color_enabled': True,
                'verbose_by_default': False
            },
            'performance': {
                'lazy_loading': True,
                'memory_limit_mb': 512,
                'max_concurrent_operations': 4
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
    
    def _create_environment_configs(self):
        """Create environment-specific configurations"""
        environments = {
            'development': {
                'logging': {'level': 'DEBUG', 'console_enabled': True},
                'optimization': {'cache_enabled': False},
                'ui': {'verbose_by_default': True}
            },
            'production': {
                'logging': {'level': 'WARNING', 'console_enabled': False},
                'optimization': {'cache_enabled': True},
                'performance': {'memory_limit_mb': 256}
            },
            'testing': {
                'logging': {'level': 'ERROR', 'file_enabled': False},
                'optimization': {'cache_enabled': False},
                'ui': {'progress_enabled': False}
            }
        }
        
        for env_name, env_config in environments.items():
            env_file = self.env_dir / f'{env_name}.yaml'
            if not env_file.exists():
                with open(env_file, 'w') as f:
                    yaml.dump(env_config, f, default_flow_style=False, indent=2)
    
    def get_config(self, reload: bool = False) -> Dict[str, Any]:
        """Get merged configuration (base + environment)"""
        if self._config_cache is None or reload:
            self._config_cache = self._load_merged_config()
        return self._config_cache
    
    def _load_merged_config(self) -> Dict[str, Any]:
        """Load and merge base config with environment config"""
        # Load and validate base config
        try:
            base_config = ConfigValidator.validate_config_file(self.config_file)
        except ConfigurationError:
            # Fall back to default config if validation fails
            base_config = ConfigValidator.get_default_config()
        
        # Load environment config
        env_name = base_config.get('environment', 'production')
        env_file = self.env_dir / f'{env_name}.yaml'
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_config = yaml.safe_load(f)
            
            # Deep merge configurations
            merged_config = self._deep_merge(base_config, env_config)
        else:
            merged_config = base_config
        
        return merged_config
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def set_config(self, key_path: str, value: Any, environment: Optional[str] = None):
        """Set configuration value using dot notation (e.g., 'logging.level')"""
        if environment:
            config_file = self.env_dir / f'{environment}.yaml'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f) or {}
            else:
                config = {}
        else:
            config_file = self.config_file
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
        
        # Navigate to the key using dot notation
        keys = key_path.split('.')
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        
        # Save updated config
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        # Clear cache
        self._config_cache = None
    
    def get_value(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        config = self.get_config()
        keys = key_path.split('.')
        current = config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set_environment(self, environment: str):
        """Switch to different environment"""
        self.set_config('environment', environment)
    
    def list_environments(self) -> list:
        """List available environments"""
        return [f.stem for f in self.env_dir.glob('*.yaml')]
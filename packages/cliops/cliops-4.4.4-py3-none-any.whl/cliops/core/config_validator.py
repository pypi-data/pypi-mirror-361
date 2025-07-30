"""
Configuration validation for cliops
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from .exceptions import ConfigurationError

class ConfigValidator:
    """Validates cliops configuration files"""
    
    REQUIRED_SECTIONS = ['logging', 'optimization', 'ui', 'performance']
    
    VALID_LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    VALID_PATTERNS = ['adaptive_generation', 'precision_engineering', 'context_aware_generation']
    VALID_ENVIRONMENTS = ['development', 'production', 'testing']
    
    SCHEMA = {
        'version': str,
        'environment': str,
        'logging': {
            'level': str,
            'file_enabled': bool,
            'console_enabled': bool
        },
        'optimization': {
            'default_pattern': str,
            'cache_enabled': bool,
            'cache_ttl': int,
            'plugins_enabled': bool
        },
        'ui': {
            'progress_enabled': bool,
            'color_enabled': bool,
            'verbose_by_default': bool
        },
        'performance': {
            'lazy_loading': bool,
            'memory_limit_mb': int,
            'max_concurrent_operations': int
        }
    }
    
    @classmethod
    def validate_config_file(cls, config_path: Path) -> Dict[str, Any]:
        """Validate configuration file and return parsed config"""
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in config file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to read config file: {e}")
        
        if not isinstance(config, dict):
            raise ConfigurationError("Configuration must be a dictionary")
        
        # Validate structure
        cls._validate_structure(config)
        
        # Validate values
        cls._validate_values(config)
        
        return config
    
    @classmethod
    def _validate_structure(cls, config: Dict[str, Any]) -> None:
        """Validate configuration structure"""
        missing_sections = []
        for section in cls.REQUIRED_SECTIONS:
            if section not in config:
                missing_sections.append(section)
        
        if missing_sections:
            raise ConfigurationError(f"Missing required sections: {', '.join(missing_sections)}")
        
        # Validate nested structure
        for section, expected_keys in cls.SCHEMA.items():
            if section in config and isinstance(expected_keys, dict):
                section_config = config[section]
                if not isinstance(section_config, dict):
                    raise ConfigurationError(f"Section '{section}' must be a dictionary")
                
                for key, expected_type in expected_keys.items():
                    if key in section_config:
                        value = section_config[key]
                        if not isinstance(value, expected_type):
                            raise ConfigurationError(
                                f"Invalid type for {section}.{key}: expected {expected_type.__name__}, got {type(value).__name__}"
                            )
    
    @classmethod
    def _validate_values(cls, config: Dict[str, Any]) -> None:
        """Validate configuration values"""
        # Validate environment
        if 'environment' in config:
            env = config['environment']
            if env not in cls.VALID_ENVIRONMENTS:
                raise ConfigurationError(f"Invalid environment '{env}'. Valid options: {', '.join(cls.VALID_ENVIRONMENTS)}")
        
        # Validate logging level
        if 'logging' in config and 'level' in config['logging']:
            level = config['logging']['level']
            if level not in cls.VALID_LOG_LEVELS:
                raise ConfigurationError(f"Invalid log level '{level}'. Valid options: {', '.join(cls.VALID_LOG_LEVELS)}")
        
        # Validate default pattern
        if 'optimization' in config and 'default_pattern' in config['optimization']:
            pattern = config['optimization']['default_pattern']
            if pattern not in cls.VALID_PATTERNS:
                raise ConfigurationError(f"Invalid default pattern '{pattern}'. Valid options: {', '.join(cls.VALID_PATTERNS)}")
        
        # Validate memory limit
        if 'performance' in config and 'memory_limit_mb' in config['performance']:
            memory_limit = config['performance']['memory_limit_mb']
            if memory_limit < 64 or memory_limit > 8192:
                raise ConfigurationError(f"Memory limit must be between 64MB and 8192MB, got {memory_limit}MB")
        
        # Validate cache TTL
        if 'optimization' in config and 'cache_ttl' in config['optimization']:
            ttl = config['optimization']['cache_ttl']
            if ttl < 60 or ttl > 86400:
                raise ConfigurationError(f"Cache TTL must be between 60 and 86400 seconds, got {ttl}")
    
    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """Get default configuration"""
        return {
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
                'cache_ttl': 3600,
                'plugins_enabled': True
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
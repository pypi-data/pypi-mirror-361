import importlib
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from .config import Config

class PluginInterface(ABC):
    """Base interface for CliOps plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration"""
        pass
    
    @abstractmethod
    def get_patterns(self) -> Dict[str, Any]:
        """Return custom patterns provided by this plugin"""
        pass

class PluginManager:
    """Plugin discovery and management system"""
    
    def __init__(self):
        self.plugins_dir = Config.get_app_data_dir() / 'plugins'
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self._loaded_plugins: Dict[str, PluginInterface] = {}
        self._plugin_configs: Dict[str, Dict] = {}
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins"""
        plugin_files = []
        
        # Look for Python files in plugins directory
        for plugin_file in self.plugins_dir.glob('*.py'):
            if not plugin_file.name.startswith('_'):
                plugin_files.append(plugin_file.stem)
        
        # Look for plugin packages
        for plugin_dir in self.plugins_dir.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith('_'):
                init_file = plugin_dir / '__init__.py'
                if init_file.exists():
                    plugin_files.append(plugin_dir.name)
        
        return plugin_files
    
    def load_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Load a specific plugin"""
        if plugin_name in self._loaded_plugins:
            return self._loaded_plugins[plugin_name]
        
        try:
            # Add plugins directory to Python path
            if str(self.plugins_dir) not in sys.path:
                sys.path.insert(0, str(self.plugins_dir))
            
            # Import plugin module
            plugin_module = importlib.import_module(plugin_name)
            
            # Look for plugin class
            plugin_class = None
            for attr_name in dir(plugin_module):
                attr = getattr(plugin_module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, PluginInterface) and 
                    attr != PluginInterface):
                    plugin_class = attr
                    break
            
            if plugin_class is None:
                return None
            
            # Instantiate plugin
            plugin_instance = plugin_class()
            
            # Initialize with configuration
            plugin_config = self._plugin_configs.get(plugin_name, {})
            plugin_instance.initialize(plugin_config)
            
            self._loaded_plugins[plugin_name] = plugin_instance
            return plugin_instance
            
        except Exception:
            return None
    
    def load_all_plugins(self) -> Dict[str, PluginInterface]:
        """Load all discovered plugins"""
        discovered = self.discover_plugins()
        
        for plugin_name in discovered:
            self.load_plugin(plugin_name)
        
        return self._loaded_plugins.copy()
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """Get loaded plugin by name"""
        return self._loaded_plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, PluginInterface]:
        """Get all loaded plugins"""
        return self._loaded_plugins.copy()
    
    def set_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> None:
        """Set configuration for a plugin"""
        self._plugin_configs[plugin_name] = config
        
        # If plugin is already loaded, reinitialize it
        if plugin_name in self._loaded_plugins:
            self._loaded_plugins[plugin_name].initialize(config)
    
    def get_plugin_patterns(self) -> Dict[str, Any]:
        """Get all patterns from loaded plugins"""
        all_patterns = {}
        
        for plugin_name, plugin in self._loaded_plugins.items():
            try:
                plugin_patterns = plugin.get_patterns()
                for pattern_name, pattern_data in plugin_patterns.items():
                    # Prefix pattern name with plugin name to avoid conflicts
                    prefixed_name = f"{plugin_name}_{pattern_name}"
                    all_patterns[prefixed_name] = pattern_data
            except Exception:
                continue
        
        return all_patterns
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        if plugin_name in self._loaded_plugins:
            del self._loaded_plugins[plugin_name]
            return True
        return False
    
    def create_plugin_template(self, plugin_name: str) -> Path:
        """Create a template plugin file"""
        template_content = f'''"""
{plugin_name} - CliOps Plugin
"""

from cliops.core.plugin_manager import PluginInterface
from typing import Dict, Any

class {plugin_name.title()}Plugin(PluginInterface):
    """Example plugin for CliOps"""
    
    @property
    def name(self) -> str:
        return "{plugin_name}"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration"""
        self.config = config
    
    def get_patterns(self) -> Dict[str, Any]:
        """Return custom patterns provided by this plugin"""
        return {{
            "example_pattern": {{
                "name": "example_pattern",
                "description": "Example pattern from {plugin_name} plugin",
                "template": "# Example Template\\n{{directive}}\\n\\n{{code_here}}",
                "principles": ["Example Principle"]
            }}
        }}
'''
        
        plugin_file = self.plugins_dir / f"{plugin_name}.py"
        with open(plugin_file, 'w') as f:
            f.write(template_content)
        
        return plugin_file
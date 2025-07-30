"""
Paper2Data Plugin Management System

This module provides a comprehensive plugin architecture for extending Paper2Data's
processing capabilities with dynamic loading, lifecycle management, and configurable
processing pipelines.

Key Features:
- Dynamic plugin discovery and loading
- Plugin lifecycle management (load, configure, enable, disable)
- Hook-based extension system
- Plugin dependency resolution
- Configuration management
- Error handling and validation
- Performance monitoring

Example Usage:
    ```python
    from paper2data.plugin_manager import PluginManager
    
    # Initialize plugin manager
    manager = PluginManager()
    
    # Load plugins from directory
    manager.load_plugins_from_directory("./plugins")
    
    # Execute processing hooks
    result = manager.execute_hook("process_equations", equation_data)
    
    # Configure plugin
    manager.configure_plugin("latex_processor", {"output_format": "mathjax"})
    ```

Author: Paper2Data Team
Version: 1.0.0
"""

import os
import sys
import inspect
import importlib
import importlib.util
from typing import Dict, List, Any, Optional, Callable, Union, Type, Set
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import yaml
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import traceback
from functools import wraps


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginStatus(Enum):
    """Plugin status enumeration"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"


class HookPriority(Enum):
    """Hook execution priority levels"""
    LOWEST = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    HIGHEST = 100


@dataclass
class PluginMetadata:
    """Plugin metadata information"""
    name: str
    version: str
    description: str
    author: str
    license: str = "MIT"
    website: str = ""
    dependencies: List[str] = field(default_factory=list)
    paper2data_version: str = ">=1.0.0"
    hooks: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    experimental: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "license": self.license,
            "website": self.website,
            "dependencies": self.dependencies,
            "paper2data_version": self.paper2data_version,
            "hooks": self.hooks,
            "config_schema": self.config_schema,
            "tags": self.tags,
            "experimental": self.experimental
        }


@dataclass
class PluginInfo:
    """Complete plugin information"""
    metadata: PluginMetadata
    status: PluginStatus
    file_path: str
    module: Optional[Any] = None
    plugin_class: Optional[Type] = None
    instance: Optional[Any] = None
    config: Dict[str, Any] = field(default_factory=dict)
    load_time: Optional[float] = None
    error_message: Optional[str] = None
    execution_count: int = 0
    total_execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plugin info to dictionary"""
        return {
            "metadata": self.metadata.to_dict(),
            "status": self.status.value,
            "file_path": self.file_path,
            "config": self.config,
            "load_time": self.load_time,
            "error_message": self.error_message,
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time
        }


@dataclass
class HookRegistration:
    """Hook registration information"""
    plugin_name: str
    hook_name: str
    callback: Callable
    priority: HookPriority
    description: str = ""
    
    def __post_init__(self):
        if not callable(self.callback):
            raise ValueError(f"Hook callback must be callable, got {type(self.callback)}")


class PluginError(Exception):
    """Base exception for plugin-related errors"""
    pass


class PluginLoadError(PluginError):
    """Exception raised when plugin loading fails"""
    pass


class PluginConfigError(PluginError):
    """Exception raised when plugin configuration is invalid"""
    pass


class HookExecutionError(PluginError):
    """Exception raised when hook execution fails"""
    pass


class BasePlugin(ABC):
    """
    Base class for all Paper2Data plugins
    
    All plugins must inherit from this class and implement the required methods.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the plugin
        
        Args:
            config: Plugin configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(f"plugin.{self.__class__.__name__}")
        self.enabled = True
        self._setup_complete = False
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Return plugin metadata
        
        Returns:
            PluginMetadata: Complete plugin metadata
        """
        pass
    
    @abstractmethod
    def setup(self) -> bool:
        """
        Set up the plugin (called after loading)
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """
        Clean up plugin resources (called before unloading)
        
        Returns:
            bool: True if cleanup successful, False otherwise
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate plugin configuration
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        # Default implementation - can be overridden by plugins
        return True
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Return JSON schema for plugin configuration
        
        Returns:
            Dict[str, Any]: JSON schema for configuration validation
        """
        return {}
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self.enabled
    
    def enable(self):
        """Enable the plugin"""
        self.enabled = True
        self.logger.info(f"Plugin {self.__class__.__name__} enabled")
    
    def disable(self):
        """Disable the plugin"""
        self.enabled = False
        self.logger.info(f"Plugin {self.__class__.__name__} disabled")
    
    def get_version(self) -> str:
        """Get plugin version"""
        return self.get_metadata().version
    
    def get_description(self) -> str:
        """Get plugin description"""
        return self.get_metadata().description


def plugin_hook(hook_name: str, priority: HookPriority = HookPriority.NORMAL, 
                description: str = ""):
    """
    Decorator for registering plugin hook methods
    
    Args:
        hook_name: Name of the hook to register
        priority: Execution priority for the hook
        description: Description of the hook function
    """
    def decorator(func: Callable) -> Callable:
        func._plugin_hook_name = hook_name
        func._plugin_hook_priority = priority
        func._plugin_hook_description = description
        return func
    return decorator


class PluginManager:
    """
    Central plugin management system for Paper2Data
    
    Handles plugin discovery, loading, configuration, and execution.
    """
    
    def __init__(self, plugin_dirs: List[str] = None, config_file: str = None):
        """
        Initialize the plugin manager
        
        Args:
            plugin_dirs: List of directories to search for plugins
            config_file: Path to plugin configuration file
        """
        self.plugin_dirs = plugin_dirs or []
        self.config_file = config_file
        self.plugins: Dict[str, PluginInfo] = {}
        self.hooks: Dict[str, List[HookRegistration]] = {}
        self.plugin_config: Dict[str, Dict[str, Any]] = {}
        self.load_order: List[str] = []
        self.logger = logging.getLogger("PluginManager")
        
        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_configuration(config_file)
    
    def add_plugin_directory(self, directory: str):
        """
        Add a directory to search for plugins
        
        Args:
            directory: Path to plugin directory
        """
        if os.path.exists(directory) and directory not in self.plugin_dirs:
            self.plugin_dirs.append(directory)
            self.logger.info(f"Added plugin directory: {directory}")
    
    def load_configuration(self, config_file: str):
        """
        Load plugin configuration from file
        
        Args:
            config_file: Path to configuration file (JSON or YAML)
        """
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.json'):
                    config = json.load(f)
                elif config_file.endswith(('.yml', '.yaml')):
                    config = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported configuration format: {config_file}")
            
            self.plugin_config = config.get('plugins', {})
            self.load_order = config.get('load_order', [])
            
            self.logger.info(f"Loaded configuration from {config_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise PluginConfigError(f"Failed to load configuration: {e}")
    
    def discover_plugins(self, directory: str = None) -> List[str]:
        """
        Discover plugin files in specified directory
        
        Args:
            directory: Directory to search (if None, searches all configured directories)
            
        Returns:
            List[str]: List of discovered plugin file paths
        """
        plugin_files = []
        search_dirs = [directory] if directory else self.plugin_dirs
        
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
                
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if file.endswith('_plugin.py') or file.endswith('_plugin.pyo'):
                        plugin_files.append(os.path.join(root, file))
        
        self.logger.info(f"Discovered {len(plugin_files)} plugin files")
        return plugin_files
    
    def load_plugin_from_file(self, file_path: str) -> Optional[PluginInfo]:
        """
        Load a plugin from a Python file
        
        Args:
            file_path: Path to plugin file
            
        Returns:
            Optional[PluginInfo]: Loaded plugin information or None if failed
        """
        try:
            start_time = time.time()
            
            # Generate module name from file path
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Cannot load module spec from {file_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class (must inherit from BasePlugin)
            plugin_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj is not BasePlugin):
                    plugin_class = obj
                    break
            
            if plugin_class is None:
                raise PluginLoadError(f"No plugin class found in {file_path}")
            
            # Create plugin instance
            plugin_config = self.plugin_config.get(module_name, {})
            plugin_instance = plugin_class(plugin_config)
            
            # Get metadata
            metadata = plugin_instance.get_metadata()
            
            # Validate metadata
            if not isinstance(metadata, PluginMetadata):
                raise PluginLoadError(f"Invalid metadata type: {type(metadata)}")
            
            # Setup plugin
            if not plugin_instance.setup():
                raise PluginLoadError(f"Plugin setup failed for {metadata.name}")
            
            load_time = time.time() - start_time
            
            # Create plugin info
            plugin_info = PluginInfo(
                metadata=metadata,
                status=PluginStatus.LOADED,
                file_path=file_path,
                module=module,
                plugin_class=plugin_class,
                instance=plugin_instance,
                config=plugin_config,
                load_time=load_time
            )
            
            # Register plugin hooks
            self._register_plugin_hooks(plugin_info)
            
            self.plugins[metadata.name] = plugin_info
            self.logger.info(f"Loaded plugin '{metadata.name}' v{metadata.version} "
                           f"in {load_time:.2f}s")
            
            return plugin_info
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin from {file_path}: {e}")
            
            # Create error plugin info
            error_info = PluginInfo(
                metadata=PluginMetadata(
                    name=os.path.basename(file_path),
                    version="unknown",
                    description="Failed to load",
                    author="unknown"
                ),
                status=PluginStatus.ERROR,
                file_path=file_path,
                error_message=str(e)
            )
            
            return error_info
    
    def _register_plugin_hooks(self, plugin_info: PluginInfo):
        """
        Register hooks for a loaded plugin
        
        Args:
            plugin_info: Plugin information
        """
        if plugin_info.instance is None:
            return
        
        # Find methods with hook decorators
        for method_name in dir(plugin_info.instance):
            method = getattr(plugin_info.instance, method_name)
            
            if (hasattr(method, '_plugin_hook_name') and 
                callable(method)):
                
                hook_name = method._plugin_hook_name
                priority = getattr(method, '_plugin_hook_priority', HookPriority.NORMAL)
                description = getattr(method, '_plugin_hook_description', "")
                
                # Register the hook
                hook_reg = HookRegistration(
                    plugin_name=plugin_info.metadata.name,
                    hook_name=hook_name,
                    callback=method,
                    priority=priority,
                    description=description
                )
                
                if hook_name not in self.hooks:
                    self.hooks[hook_name] = []
                
                self.hooks[hook_name].append(hook_reg)
                
                self.logger.debug(f"Registered hook '{hook_name}' for plugin "
                                f"'{plugin_info.metadata.name}'")
        
        # Sort hooks by priority
        for hook_name in self.hooks:
            self.hooks[hook_name].sort(key=lambda x: x.priority.value, reverse=True)
    
    def load_plugins_from_directory(self, directory: str) -> Dict[str, PluginInfo]:
        """
        Load all plugins from a directory
        
        Args:
            directory: Directory containing plugin files
            
        Returns:
            Dict[str, PluginInfo]: Dictionary mapping plugin names to plugin info
        """
        if not os.path.exists(directory):
            self.logger.warning(f"Plugin directory does not exist: {directory}")
            return {}
        
        self.add_plugin_directory(directory)
        plugin_files = self.discover_plugins(directory)
        loaded_plugins = {}
        
        for file_path in plugin_files:
            plugin_info = self.load_plugin_from_file(file_path)
            if plugin_info and plugin_info.status != PluginStatus.ERROR:
                loaded_plugins[plugin_info.metadata.name] = plugin_info
        
        self.logger.info(f"Loaded {len(loaded_plugins)} plugins from {directory}")
        return loaded_plugins
    
    def load_all_plugins(self) -> Dict[str, PluginInfo]:
        """
        Load all plugins from all configured directories
        
        Returns:
            Dict[str, PluginInfo]: Dictionary mapping plugin names to plugin info
        """
        loaded_plugins = {}
        
        for directory in self.plugin_dirs:
            dir_plugins = self.load_plugins_from_directory(directory)
            loaded_plugins.update(dir_plugins)
        
        return loaded_plugins
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin
        
        Args:
            plugin_name: Name of plugin to unload
            
        Returns:
            bool: True if successfully unloaded, False otherwise
        """
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin '{plugin_name}' not found")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        try:
            # Cleanup plugin
            if plugin_info.instance:
                plugin_info.instance.cleanup()
            
            # Remove hooks
            for hook_name in list(self.hooks.keys()):
                self.hooks[hook_name] = [
                    reg for reg in self.hooks[hook_name] 
                    if reg.plugin_name != plugin_name
                ]
                
                # Remove empty hook lists
                if not self.hooks[hook_name]:
                    del self.hooks[hook_name]
            
            # Remove plugin
            del self.plugins[plugin_name]
            
            self.logger.info(f"Unloaded plugin '{plugin_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin '{plugin_name}': {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """
        Enable a plugin
        
        Args:
            plugin_name: Name of plugin to enable
            
        Returns:
            bool: True if successfully enabled, False otherwise
        """
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin '{plugin_name}' not found")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.instance:
            plugin_info.instance.enable()
            plugin_info.status = PluginStatus.ENABLED
            self.logger.info(f"Enabled plugin '{plugin_name}'")
            return True
        
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """
        Disable a plugin
        
        Args:
            plugin_name: Name of plugin to disable
            
        Returns:
            bool: True if successfully disabled, False otherwise
        """
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin '{plugin_name}' not found")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.instance:
            plugin_info.instance.disable()
            plugin_info.status = PluginStatus.DISABLED
            self.logger.info(f"Disabled plugin '{plugin_name}'")
            return True
        
        return False
    
    def configure_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """
        Configure a plugin
        
        Args:
            plugin_name: Name of plugin to configure
            config: Configuration dictionary
            
        Returns:
            bool: True if successfully configured, False otherwise
        """
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin '{plugin_name}' not found")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        try:
            # Validate configuration
            if plugin_info.instance and not plugin_info.instance.validate_config(config):
                raise PluginConfigError(f"Invalid configuration for plugin '{plugin_name}'")
            
            # Update configuration
            plugin_info.config.update(config)
            
            if plugin_info.instance:
                plugin_info.instance.config.update(config)
            
            self.logger.info(f"Configured plugin '{plugin_name}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure plugin '{plugin_name}': {e}")
            return False
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """
        Get information about a plugin
        
        Args:
            plugin_name: Name of plugin
            
        Returns:
            Optional[PluginInfo]: Plugin information or None if not found
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> Dict[str, PluginInfo]:
        """
        List all loaded plugins
        
        Returns:
            Dict[str, PluginInfo]: Dictionary mapping plugin names to plugin info
        """
        return self.plugins.copy()
    
    def list_hooks(self) -> Dict[str, List[HookRegistration]]:
        """
        List all registered hooks
        
        Returns:
            Dict[str, List[HookRegistration]]: Dictionary mapping hook names to registrations
        """
        return self.hooks.copy()
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """
        Execute all callbacks for a specific hook
        
        Args:
            hook_name: Name of hook to execute
            *args: Positional arguments to pass to hook callbacks
            **kwargs: Keyword arguments to pass to hook callbacks
            
        Returns:
            List[Any]: List of results from hook callbacks
        """
        if hook_name not in self.hooks:
            return []
        
        results = []
        
        for hook_reg in self.hooks[hook_name]:
            # Skip disabled plugins
            plugin_info = self.plugins.get(hook_reg.plugin_name)
            if (plugin_info and plugin_info.instance and 
                not plugin_info.instance.is_enabled()):
                continue
            
            try:
                start_time = time.time()
                result = hook_reg.callback(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Update plugin statistics
                if plugin_info:
                    plugin_info.execution_count += 1
                    plugin_info.total_execution_time += execution_time
                
                results.append(result)
                
                self.logger.debug(f"Executed hook '{hook_name}' for plugin "
                                f"'{hook_reg.plugin_name}' in {execution_time:.3f}s")
                
            except Exception as e:
                self.logger.error(f"Hook '{hook_name}' failed for plugin "
                                f"'{hook_reg.plugin_name}': {e}")
                
                # Optionally disable problematic plugins
                if plugin_info:
                    plugin_info.status = PluginStatus.ERROR
                    plugin_info.error_message = str(e)
        
        return results
    
    def execute_hook_until_success(self, hook_name: str, *args, **kwargs) -> Any:
        """
        Execute hook callbacks until one returns a truthy result
        
        Args:
            hook_name: Name of hook to execute
            *args: Positional arguments to pass to hook callbacks
            **kwargs: Keyword arguments to pass to hook callbacks
            
        Returns:
            Any: First truthy result from hook callbacks, or None
        """
        if hook_name not in self.hooks:
            return None
        
        for hook_reg in self.hooks[hook_name]:
            # Skip disabled plugins
            plugin_info = self.plugins.get(hook_reg.plugin_name)
            if (plugin_info and plugin_info.instance and 
                not plugin_info.instance.is_enabled()):
                continue
            
            try:
                result = hook_reg.callback(*args, **kwargs)
                
                if result:  # Return first truthy result
                    self.logger.debug(f"Hook '{hook_name}' succeeded for plugin "
                                    f"'{hook_reg.plugin_name}'")
                    return result
                    
            except Exception as e:
                self.logger.error(f"Hook '{hook_name}' failed for plugin "
                                f"'{hook_reg.plugin_name}': {e}")
                continue
        
        return None
    
    def get_plugin_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get performance statistics for all plugins
        
        Returns:
            Dict[str, Dict[str, Any]]: Plugin statistics
        """
        stats = {}
        
        for plugin_name, plugin_info in self.plugins.items():
            stats[plugin_name] = {
                "status": plugin_info.status.value,
                "load_time": plugin_info.load_time,
                "execution_count": plugin_info.execution_count,
                "total_execution_time": plugin_info.total_execution_time,
                "average_execution_time": (
                    plugin_info.total_execution_time / plugin_info.execution_count
                    if plugin_info.execution_count > 0 else 0
                ),
                "hooks_registered": len([
                    reg for hook_list in self.hooks.values() 
                    for reg in hook_list 
                    if reg.plugin_name == plugin_name
                ])
            }
        
        return stats
    
    def export_configuration(self, file_path: str):
        """
        Export current plugin configuration to file
        
        Args:
            file_path: Path to export configuration file
        """
        config = {
            "plugins": self.plugin_config,
            "load_order": self.load_order,
            "plugin_info": {
                name: info.to_dict() 
                for name, info in self.plugins.items()
            }
        }
        
        try:
            with open(file_path, 'w') as f:
                if file_path.endswith('.json'):
                    json.dump(config, f, indent=2)
                elif file_path.endswith(('.yml', '.yaml')):
                    yaml.dump(config, f, default_flow_style=False)
                else:
                    json.dump(config, f, indent=2)
            
            self.logger.info(f"Exported configuration to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration: {e}")
            raise PluginConfigError(f"Failed to export configuration: {e}")
    
    def cleanup(self):
        """Clean up all loaded plugins"""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
        
        self.plugins.clear()
        self.hooks.clear()
        self.logger.info("Plugin manager cleaned up")


# Global plugin manager instance
_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """
    Get the global plugin manager instance
    
    Returns:
        PluginManager: Global plugin manager instance
    """
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def initialize_plugin_system(plugin_dirs: List[str] = None, 
                           config_file: str = None) -> PluginManager:
    """
    Initialize the global plugin system
    
    Args:
        plugin_dirs: List of directories to search for plugins
        config_file: Path to plugin configuration file
        
    Returns:
        PluginManager: Initialized plugin manager
    """
    global _plugin_manager
    _plugin_manager = PluginManager(plugin_dirs, config_file)
    return _plugin_manager 
"""
Paper2Data Enhanced Plugin System

This module provides an enhanced plugin system that integrates all the advanced
features including dependency management, marketplace integration, automatic
updates, and comprehensive plugin lifecycle management.

Features:
- Unified plugin management interface
- Automatic dependency resolution
- Marketplace integration
- Plugin versioning and updates
- Security validation
- Performance monitoring
- Plugin health checks
- Automatic plugin discovery
- Configuration management
- Community features integration

Author: Paper2Data Team
Version: 1.1.0
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import asyncio
from pathlib import Path
import time
from datetime import datetime, timedelta
import threading
import schedule
from concurrent.futures import ThreadPoolExecutor, as_completed

from .plugin_manager import PluginManager, PluginInfo, PluginStatus, BasePlugin
from .plugin_dependency_manager import DependencyManager, DependencyResolution
from .plugin_marketplace import PluginMarketplace, MarketplacePlugin, SearchFilter
from .plugin_hooks import execute_hook, execute_hook_until_success


logger = logging.getLogger(__name__)


class PluginSystemStatus(Enum):
    """Plugin system status"""
    INITIALIZING = "initializing"
    READY = "ready"
    UPDATING = "updating"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class PluginHealth:
    """Plugin health status"""
    plugin_name: str
    status: str
    last_check: datetime
    errors: List[str]
    performance_score: float
    memory_usage: int
    cpu_usage: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "plugin_name": self.plugin_name,
            "status": self.status,
            "last_check": self.last_check.isoformat(),
            "errors": self.errors,
            "performance_score": self.performance_score,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage
        }


@dataclass
class SystemMetrics:
    """System-wide plugin metrics"""
    total_plugins: int
    active_plugins: int
    failed_plugins: int
    total_hooks: int
    avg_response_time: float
    memory_usage: int
    uptime: timedelta
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_plugins": self.total_plugins,
            "active_plugins": self.active_plugins,
            "failed_plugins": self.failed_plugins,
            "total_hooks": self.total_hooks,
            "avg_response_time": self.avg_response_time,
            "memory_usage": self.memory_usage,
            "uptime": str(self.uptime)
        }


class EnhancedPluginSystem:
    """
    Enhanced plugin system with comprehensive management capabilities
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize enhanced plugin system
        
        Args:
            config: System configuration
        """
        self.config = config or {}
        self.logger = logging.getLogger("EnhancedPluginSystem")
        
        # System status
        self.status = PluginSystemStatus.INITIALIZING
        self.start_time = datetime.now()
        
        # Core components
        self.plugin_manager = PluginManager(
            plugin_dirs=self.config.get("plugin_dirs", ["./plugins"]),
            config_file=self.config.get("plugin_config_file")
        )
        
        self.dependency_manager = DependencyManager(
            config=self.config.get("dependency_config", {})
        )
        
        self.marketplace = PluginMarketplace(
            config=self.config.get("marketplace_config", {})
        )
        
        # Health monitoring
        self.plugin_health: Dict[str, PluginHealth] = {}
        self.health_check_interval = self.config.get("health_check_interval", 300)  # 5 minutes
        self.health_check_thread = None
        
        # Auto-update settings
        self.auto_update_enabled = self.config.get("auto_update_enabled", False)
        self.update_check_interval = self.config.get("update_check_interval", 3600)  # 1 hour
        self.update_thread = None
        
        # Performance monitoring
        self.performance_metrics: Dict[str, List[float]] = {}
        self.max_metrics_history = self.config.get("max_metrics_history", 1000)
        
        # Initialize system
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the enhanced plugin system"""
        try:
            self.logger.info("Initializing enhanced plugin system")
            
            # Load existing plugins
            self.plugin_manager.load_all_plugins()
            
            # Start health monitoring
            if self.config.get("health_monitoring_enabled", True):
                self._start_health_monitoring()
            
            # Start auto-update monitoring
            if self.auto_update_enabled:
                self._start_auto_update_monitoring()
            
            # Initial health check
            self._check_all_plugin_health()
            
            self.status = PluginSystemStatus.READY
            self.logger.info("Enhanced plugin system initialized successfully")
            
        except Exception as e:
            self.status = PluginSystemStatus.ERROR
            self.logger.error(f"Failed to initialize enhanced plugin system: {e}")
            raise
    
    def _start_health_monitoring(self):
        """Start health monitoring background thread"""
        def health_monitor():
            schedule.every(self.health_check_interval).seconds.do(self._check_all_plugin_health)
            
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for scheduled tasks
        
        self.health_check_thread = threading.Thread(target=health_monitor, daemon=True)
        self.health_check_thread.start()
        self.logger.info("Health monitoring started")
    
    def _start_auto_update_monitoring(self):
        """Start auto-update monitoring background thread"""
        def update_monitor():
            schedule.every(self.update_check_interval).seconds.do(self._check_for_updates)
            
            while True:
                schedule.run_pending()
                time.sleep(300)  # Check every 5 minutes for scheduled tasks
        
        self.update_thread = threading.Thread(target=update_monitor, daemon=True)
        self.update_thread.start()
        self.logger.info("Auto-update monitoring started")
    
    def _check_all_plugin_health(self):
        """Check health of all plugins"""
        try:
            for plugin_name, plugin_info in self.plugin_manager.plugins.items():
                health = self._check_plugin_health(plugin_name, plugin_info)
                self.plugin_health[plugin_name] = health
                
                # Log critical health issues
                if health.status == "error":
                    self.logger.warning(f"Plugin {plugin_name} has health issues: {health.errors}")
                    
        except Exception as e:
            self.logger.error(f"Failed to check plugin health: {e}")
    
    def _check_plugin_health(self, plugin_name: str, plugin_info: PluginInfo) -> PluginHealth:
        """Check health of a specific plugin"""
        try:
            errors = []
            performance_score = 1.0
            
            # Check if plugin is loaded
            if plugin_info.status != PluginStatus.ENABLED:
                errors.append(f"Plugin not enabled: {plugin_info.status.value}")
                performance_score *= 0.5
            
            # Check plugin instance
            if not plugin_info.instance:
                errors.append("Plugin instance not available")
                performance_score *= 0.3
            
            # Check plugin configuration
            if plugin_info.instance:
                try:
                    config_valid = plugin_info.instance.validate_config(plugin_info.config)
                    if not config_valid:
                        errors.append("Invalid plugin configuration")
                        performance_score *= 0.7
                except Exception as e:
                    errors.append(f"Configuration validation error: {e}")
                    performance_score *= 0.6
            
            # Check recent errors
            if plugin_info.error_message:
                errors.append(f"Recent error: {plugin_info.error_message}")
                performance_score *= 0.4
            
            # Calculate performance score based on execution metrics
            if plugin_info.execution_count > 0:
                avg_time = plugin_info.total_execution_time / plugin_info.execution_count
                # Penalize slow plugins
                if avg_time > 1.0:  # > 1 second average
                    performance_score *= max(0.2, 1.0 - (avg_time - 1.0) * 0.1)
            
            status = "healthy" if not errors else "error"
            
            return PluginHealth(
                plugin_name=plugin_name,
                status=status,
                last_check=datetime.now(),
                errors=errors,
                performance_score=performance_score,
                memory_usage=0,  # Would need actual memory monitoring
                cpu_usage=0.0   # Would need actual CPU monitoring
            )
            
        except Exception as e:
            self.logger.error(f"Failed to check health for plugin {plugin_name}: {e}")
            return PluginHealth(
                plugin_name=plugin_name,
                status="error",
                last_check=datetime.now(),
                errors=[f"Health check failed: {e}"],
                performance_score=0.0,
                memory_usage=0,
                cpu_usage=0.0
            )
    
    async def _check_for_updates(self):
        """Check for plugin updates"""
        try:
            self.logger.info("Checking for plugin updates")
            
            # Refresh marketplace
            await self.marketplace.refresh_plugin_list()
            
            # Check each installed plugin
            installed_plugins = self.plugin_manager.list_plugins()
            
            for plugin_name, plugin_info in installed_plugins.items():
                marketplace_plugin = self.marketplace.get_plugin_details(plugin_name)
                
                if marketplace_plugin:
                    # Compare versions (simplified)
                    if marketplace_plugin.version != plugin_info.metadata.version:
                        self.logger.info(f"Update available for {plugin_name}: {marketplace_plugin.version}")
                        
                        # Auto-update if enabled
                        if self.auto_update_enabled:
                            await self.update_plugin(plugin_name)
                            
        except Exception as e:
            self.logger.error(f"Failed to check for updates: {e}")
    
    async def install_plugin(self, plugin_name: str, 
                           version: str = None,
                           from_marketplace: bool = True) -> bool:
        """
        Install a plugin with comprehensive validation
        
        Args:
            plugin_name: Name of plugin to install
            version: Specific version to install
            from_marketplace: Whether to install from marketplace
            
        Returns:
            bool: True if installation successful
        """
        try:
            self.logger.info(f"Installing plugin {plugin_name}")
            
            if from_marketplace:
                # Install from marketplace
                success = await self.marketplace.install_plugin(plugin_name, version)
                if not success:
                    return False
                
                # Reload plugin manager to pick up new plugin
                self.plugin_manager.load_all_plugins()
            else:
                # Install from local file or directory
                # This would need additional implementation
                self.logger.error("Local plugin installation not yet implemented")
                return False
            
            # Validate installation
            if plugin_name not in self.plugin_manager.plugins:
                self.logger.error(f"Plugin {plugin_name} not found after installation")
                return False
            
            # Enable plugin
            self.plugin_manager.enable_plugin(plugin_name)
            
            # Run initial health check
            plugin_info = self.plugin_manager.plugins[plugin_name]
            health = self._check_plugin_health(plugin_name, plugin_info)
            self.plugin_health[plugin_name] = health
            
            if health.status == "error":
                self.logger.warning(f"Plugin {plugin_name} has issues after installation")
            
            self.logger.info(f"Successfully installed plugin {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install plugin {plugin_name}: {e}")
            return False
    
    async def uninstall_plugin(self, plugin_name: str, 
                             force: bool = False) -> bool:
        """
        Uninstall a plugin with dependency checking
        
        Args:
            plugin_name: Name of plugin to uninstall
            force: Force uninstall even if dependencies exist
            
        Returns:
            bool: True if uninstallation successful
        """
        try:
            self.logger.info(f"Uninstalling plugin {plugin_name}")
            
            # Check dependencies
            dependents = self.dependency_manager._find_dependents(plugin_name)
            if dependents and not force:
                self.logger.error(f"Cannot uninstall {plugin_name}: required by {dependents}")
                return False
            
            # Disable plugin first
            self.plugin_manager.disable_plugin(plugin_name)
            
            # Uninstall from dependency manager
            self.dependency_manager.uninstall_package(plugin_name, force)
            
            # Uninstall from marketplace
            await self.marketplace.uninstall_plugin(plugin_name)
            
            # Unload from plugin manager
            self.plugin_manager.unload_plugin(plugin_name)
            
            # Remove from health monitoring
            if plugin_name in self.plugin_health:
                del self.plugin_health[plugin_name]
            
            self.logger.info(f"Successfully uninstalled plugin {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall plugin {plugin_name}: {e}")
            return False
    
    async def update_plugin(self, plugin_name: str) -> bool:
        """
        Update a plugin to latest version
        
        Args:
            plugin_name: Name of plugin to update
            
        Returns:
            bool: True if update successful
        """
        try:
            self.logger.info(f"Updating plugin {plugin_name}")
            
            # Update through marketplace
            success = await self.marketplace.update_plugin(plugin_name)
            if not success:
                return False
            
            # Reload plugin
            self.plugin_manager.unload_plugin(plugin_name)
            self.plugin_manager.load_all_plugins()
            
            # Re-enable plugin
            self.plugin_manager.enable_plugin(plugin_name)
            
            # Update health status
            plugin_info = self.plugin_manager.plugins[plugin_name]
            health = self._check_plugin_health(plugin_name, plugin_info)
            self.plugin_health[plugin_name] = health
            
            self.logger.info(f"Successfully updated plugin {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update plugin {plugin_name}: {e}")
            return False
    
    def search_plugins(self, query: str = "", 
                      category: str = None,
                      min_rating: float = None,
                      limit: int = 20) -> List[MarketplacePlugin]:
        """
        Search for plugins in marketplace
        
        Args:
            query: Search query
            category: Plugin category
            min_rating: Minimum rating
            limit: Maximum results
            
        Returns:
            List[MarketplacePlugin]: Search results
        """
        try:
            # Create search filter
            search_filter = SearchFilter(
                min_rating=min_rating
            )
            
            if category:
                from .plugin_marketplace import PluginCategory
                search_filter.category = PluginCategory(category)
            
            # Search marketplace
            results = self.marketplace.search_plugins(
                query=query,
                filters=search_filter,
                limit=limit
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search plugins: {e}")
            return []
    
    def get_plugin_status(self, plugin_name: str) -> Dict[str, Any]:
        """
        Get comprehensive plugin status
        
        Args:
            plugin_name: Name of plugin
            
        Returns:
            Dict[str, Any]: Plugin status information
        """
        try:
            status = {
                "plugin_info": None,
                "health": None,
                "marketplace_info": None,
                "dependencies": None
            }
            
            # Plugin manager info
            plugin_info = self.plugin_manager.get_plugin_info(plugin_name)
            if plugin_info:
                status["plugin_info"] = plugin_info.to_dict()
            
            # Health info
            if plugin_name in self.plugin_health:
                status["health"] = self.plugin_health[plugin_name].to_dict()
            
            # Marketplace info
            marketplace_plugin = self.marketplace.get_plugin_details(plugin_name)
            if marketplace_plugin:
                status["marketplace_info"] = marketplace_plugin.to_dict()
            
            # Dependency info
            # This would need integration with dependency manager
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get plugin status: {e}")
            return {}
    
    def get_system_metrics(self) -> SystemMetrics:
        """
        Get system-wide metrics
        
        Returns:
            SystemMetrics: System metrics
        """
        try:
            plugins = self.plugin_manager.list_plugins()
            
            total_plugins = len(plugins)
            active_plugins = sum(1 for p in plugins.values() if p.status == PluginStatus.ENABLED)
            failed_plugins = sum(1 for p in plugins.values() if p.status == PluginStatus.ERROR)
            
            # Calculate average response time
            total_time = sum(p.total_execution_time for p in plugins.values())
            total_count = sum(p.execution_count for p in plugins.values())
            avg_response_time = total_time / total_count if total_count > 0 else 0
            
            # Get hook count
            hooks = self.plugin_manager.list_hooks()
            total_hooks = sum(len(hook_list) for hook_list in hooks.values())
            
            return SystemMetrics(
                total_plugins=total_plugins,
                active_plugins=active_plugins,
                failed_plugins=failed_plugins,
                total_hooks=total_hooks,
                avg_response_time=avg_response_time,
                memory_usage=0,  # Would need actual memory monitoring
                uptime=datetime.now() - self.start_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return SystemMetrics(0, 0, 0, 0, 0, 0, timedelta(0))
    
    def get_plugin_recommendations(self, category: str = None) -> List[MarketplacePlugin]:
        """
        Get plugin recommendations based on usage patterns
        
        Args:
            category: Plugin category to filter by
            
        Returns:
            List[MarketplacePlugin]: Recommended plugins
        """
        try:
            # Simple recommendation based on ratings and downloads
            search_filter = SearchFilter(min_rating=4.0)
            
            if category:
                from .plugin_marketplace import PluginCategory
                search_filter.category = PluginCategory(category)
            
            recommendations = self.marketplace.search_plugins(
                query="",
                filters=search_filter,
                sort_by="rating",
                limit=10
            )
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Failed to get recommendations: {e}")
            return []
    
    def export_system_state(self, file_path: str):
        """
        Export complete system state to file
        
        Args:
            file_path: Path to export file
        """
        try:
            state = {
                "system_info": {
                    "status": self.status.value,
                    "start_time": self.start_time.isoformat(),
                    "config": self.config
                },
                "plugins": {
                    name: info.to_dict() 
                    for name, info in self.plugin_manager.plugins.items()
                },
                "health": {
                    name: health.to_dict() 
                    for name, health in self.plugin_health.items()
                },
                "metrics": self.get_system_metrics().to_dict(),
                "dependencies": self.dependency_manager.get_dependency_graph()
            }
            
            with open(file_path, 'w') as f:
                json.dump(state, f, indent=2)
                
            self.logger.info(f"Exported system state to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export system state: {e}")
    
    def cleanup(self):
        """Cleanup system resources"""
        try:
            self.logger.info("Cleaning up enhanced plugin system")
            
            # Stop monitoring threads
            if self.health_check_thread:
                # In a real implementation, would use proper thread shutdown
                pass
            
            if self.update_thread:
                # In a real implementation, would use proper thread shutdown
                pass
            
            # Cleanup plugin manager
            self.plugin_manager.cleanup()
            
            self.logger.info("Enhanced plugin system cleanup complete")
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup system: {e}")


# Global enhanced plugin system instance
enhanced_plugin_system = None


def get_enhanced_plugin_system() -> EnhancedPluginSystem:
    """Get global enhanced plugin system instance"""
    global enhanced_plugin_system
    if enhanced_plugin_system is None:
        enhanced_plugin_system = EnhancedPluginSystem()
    return enhanced_plugin_system


def initialize_enhanced_plugin_system(config: Dict[str, Any] = None) -> EnhancedPluginSystem:
    """
    Initialize enhanced plugin system with configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        EnhancedPluginSystem: Initialized system
    """
    global enhanced_plugin_system
    enhanced_plugin_system = EnhancedPluginSystem(config)
    return enhanced_plugin_system 
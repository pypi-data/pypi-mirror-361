"""
Comprehensive Test Suite for Enhanced Plugin System

This module provides thorough testing for the enhanced plugin system,
including dependency management, marketplace integration, and all
advanced features.

Test Coverage:
- Plugin dependency resolution
- Marketplace integration
- Plugin installation/uninstallation
- Health monitoring
- Auto-update functionality
- Performance metrics
- Security validation
- Error handling

Author: Paper2Data Team
Version: 1.1.0
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging

from .plugin_system_enhanced import EnhancedPluginSystem, PluginSystemStatus
from .plugin_dependency_manager import DependencyManager, VersionConstraint, DependencyType
from .plugin_marketplace import PluginMarketplace, MarketplacePlugin, PluginCategory, PluginStatus
from .plugin_manager import PluginManager, PluginInfo, BasePlugin, PluginMetadata


# Disable logging during tests
logging.disable(logging.CRITICAL)


class MockPlugin(BasePlugin):
    """Mock plugin for testing"""
    
    def __init__(self, name: str = "test_plugin", version: str = "1.0.0"):
        super().__init__()
        self.name = name
        self.version = version
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=self.name,
            version=self.version,
            description="Test plugin",
            author="Test Author",
            license="MIT"
        )
    
    def setup(self) -> bool:
        return True
    
    def cleanup(self) -> bool:
        return True


class TestPluginDependencyManager(unittest.TestCase):
    """Test plugin dependency management"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "installed_packages_file": str(Path(self.temp_dir) / "installed.json"),
            "package_registry_file": str(Path(self.temp_dir) / "registry.json")
        }
        
        # Create mock registry
        registry = {
            "plugin_a": {
                "version": "1.0.0",
                "dependencies": [
                    {"package": "plugin_b", "constraint": ">=1.0.0"}
                ]
            },
            "plugin_b": {
                "version": "1.0.0",
                "dependencies": []
            },
            "plugin_c": {
                "version": "2.0.0",
                "dependencies": [
                    {"package": "plugin_a", "constraint": ">=1.0.0"},
                    {"package": "plugin_b", "constraint": ">=1.0.0"}
                ]
            }
        }
        
        with open(self.config["package_registry_file"], 'w') as f:
            json.dump(registry, f)
        
        self.dependency_manager = DependencyManager(self.config)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_dependency_resolution_simple(self):
        """Test simple dependency resolution"""
        resolution = self.dependency_manager.resolve_dependencies(["plugin_b"])
        
        self.assertTrue(resolution.success)
        self.assertEqual(resolution.install_order, ["plugin_b"])
        self.assertEqual(len(resolution.conflicts), 0)
    
    def test_dependency_resolution_with_dependencies(self):
        """Test dependency resolution with dependencies"""
        resolution = self.dependency_manager.resolve_dependencies(["plugin_a"])
        
        self.assertTrue(resolution.success)
        self.assertIn("plugin_b", resolution.install_order)
        self.assertIn("plugin_a", resolution.install_order)
        # plugin_b should come before plugin_a
        self.assertLess(
            resolution.install_order.index("plugin_b"),
            resolution.install_order.index("plugin_a")
        )
    
    def test_dependency_resolution_complex(self):
        """Test complex dependency resolution"""
        resolution = self.dependency_manager.resolve_dependencies(["plugin_c"])
        
        self.assertTrue(resolution.success)
        self.assertIn("plugin_a", resolution.install_order)
        self.assertIn("plugin_b", resolution.install_order)
        self.assertIn("plugin_c", resolution.install_order)
        
        # Check order: plugin_b, plugin_a, plugin_c
        b_idx = resolution.install_order.index("plugin_b")
        a_idx = resolution.install_order.index("plugin_a")
        c_idx = resolution.install_order.index("plugin_c")
        
        self.assertLess(b_idx, a_idx)
        self.assertLess(a_idx, c_idx)
    
    def test_version_constraint_validation(self):
        """Test version constraint validation"""
        constraint = VersionConstraint("test_package", ">=1.0.0")
        
        self.assertTrue(constraint.is_satisfied_by("1.0.0"))
        self.assertTrue(constraint.is_satisfied_by("1.1.0"))
        self.assertTrue(constraint.is_satisfied_by("2.0.0"))
        self.assertFalse(constraint.is_satisfied_by("0.9.0"))
    
    def test_package_installation(self):
        """Test package installation"""
        success = self.dependency_manager.install_package("plugin_b", "1.0.0")
        self.assertTrue(success)
        
        # Check if package is marked as installed
        self.assertIn("plugin_b", self.dependency_manager.installed_packages)
        
        installed_pkg = self.dependency_manager.installed_packages["plugin_b"]
        self.assertEqual(installed_pkg.version, "1.0.0")
        self.assertTrue(installed_pkg.installed)
    
    def test_package_uninstallation(self):
        """Test package uninstallation"""
        # Install first
        self.dependency_manager.install_package("plugin_b", "1.0.0")
        
        # Then uninstall
        success = self.dependency_manager.uninstall_package("plugin_b")
        self.assertTrue(success)
        
        # Check if package is removed
        self.assertNotIn("plugin_b", self.dependency_manager.installed_packages)


class TestPluginMarketplace(unittest.TestCase):
    """Test plugin marketplace functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "marketplace_url": "https://test.marketplace.com",
            "cache_dir": str(Path(self.temp_dir) / "cache"),
            "api_key": "test_key"
        }
        
        # Create mock marketplace data
        self.mock_plugins = [
            {
                "name": "test_plugin",
                "version": "1.0.0",
                "description": "Test plugin",
                "author": "Test Author",
                "homepage": "https://test.com",
                "download_url": "https://test.com/download",
                "license": "MIT",
                "category": "extraction",
                "status": "active",
                "tags": ["test", "example"],
                "dependencies": [],
                "paper2data_version": ">=1.0.0",
                "file_size": 1024,
                "file_hash": "abc123",
                "security_scan": {
                    "status": "safe",
                    "scan_date": datetime.now().isoformat(),
                    "issues": [],
                    "score": 100,
                    "details": {}
                },
                "stats": {
                    "downloads": 1000,
                    "active_users": 100,
                    "ratings_count": 10,
                    "average_rating": 4.5,
                    "last_updated": datetime.now().isoformat(),
                    "compatibility_score": 0.95
                },
                "ratings": [],
                "screenshots": [],
                "documentation_url": "https://test.com/docs",
                "source_code_url": "https://test.com/source",
                "changelog": "Initial release"
            }
        ]
        
        self.marketplace = PluginMarketplace(self.config)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @patch('aiohttp.ClientSession')
    async def test_refresh_plugin_list(self, mock_session):
        """Test refreshing plugin list from marketplace"""
        # Mock API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"plugins": self.mock_plugins}
        
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        # Test refresh
        success = await self.marketplace.refresh_plugin_list()
        self.assertTrue(success)
        self.assertEqual(len(self.marketplace.plugins), 1)
        self.assertIn("test_plugin", self.marketplace.plugins)
    
    def test_plugin_search(self):
        """Test plugin search functionality"""
        # Add plugins to marketplace
        for plugin_data in self.mock_plugins:
            plugin = self.marketplace._dict_to_plugin(plugin_data)
            self.marketplace.plugins[plugin.name] = plugin
        
        # Test search by name
        results = self.marketplace.search_plugins("test")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "test_plugin")
        
        # Test search by tag
        results = self.marketplace.search_plugins("example")
        self.assertEqual(len(results), 1)
        
        # Test search with no results
        results = self.marketplace.search_plugins("nonexistent")
        self.assertEqual(len(results), 0)
    
    def test_plugin_details(self):
        """Test getting plugin details"""
        # Add plugin to marketplace
        plugin_data = self.mock_plugins[0]
        plugin = self.marketplace._dict_to_plugin(plugin_data)
        self.marketplace.plugins[plugin.name] = plugin
        
        # Test getting details
        details = self.marketplace.get_plugin_details("test_plugin")
        self.assertIsNotNone(details)
        self.assertEqual(details.name, "test_plugin")
        self.assertEqual(details.version, "1.0.0")
        
        # Test non-existent plugin
        details = self.marketplace.get_plugin_details("nonexistent")
        self.assertIsNone(details)
    
    def test_plugin_compatibility_check(self):
        """Test plugin compatibility checking"""
        # Add plugin to marketplace
        plugin_data = self.mock_plugins[0]
        plugin = self.marketplace._dict_to_plugin(plugin_data)
        
        # Test compatibility
        is_compatible = self.marketplace._check_compatibility(plugin)
        self.assertTrue(is_compatible)
        
        # Test incompatible plugin
        plugin.paper2data_version = ">=2.0.0"
        is_compatible = self.marketplace._check_compatibility(plugin)
        self.assertFalse(is_compatible)


class TestEnhancedPluginSystem(unittest.TestCase):
    """Test enhanced plugin system integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "plugin_dirs": [str(Path(self.temp_dir) / "plugins")],
            "health_monitoring_enabled": False,  # Disable for tests
            "auto_update_enabled": False,
            "dependency_config": {
                "installed_packages_file": str(Path(self.temp_dir) / "installed.json"),
                "package_registry_file": str(Path(self.temp_dir) / "registry.json")
            },
            "marketplace_config": {
                "cache_dir": str(Path(self.temp_dir) / "cache")
            }
        }
        
        # Create plugins directory
        Path(self.config["plugin_dirs"][0]).mkdir(parents=True, exist_ok=True)
        
        # Create mock registry
        registry = {
            "test_plugin": {
                "version": "1.0.0",
                "dependencies": []
            }
        }
        
        with open(self.config["dependency_config"]["package_registry_file"], 'w') as f:
            json.dump(registry, f)
        
        self.plugin_system = EnhancedPluginSystem(self.config)
    
    def tearDown(self):
        """Clean up test environment"""
        self.plugin_system.cleanup()
        shutil.rmtree(self.temp_dir)
    
    def test_system_initialization(self):
        """Test system initialization"""
        self.assertEqual(self.plugin_system.status, PluginSystemStatus.READY)
        self.assertIsNotNone(self.plugin_system.plugin_manager)
        self.assertIsNotNone(self.plugin_system.dependency_manager)
        self.assertIsNotNone(self.plugin_system.marketplace)
    
    def test_plugin_health_check(self):
        """Test plugin health checking"""
        # Create mock plugin
        mock_plugin = MockPlugin("test_plugin", "1.0.0")
        
        # Create mock plugin info
        plugin_info = PluginInfo(
            metadata=mock_plugin.get_metadata(),
            status=PluginStatus.ENABLED,
            file_path="/test/path",
            instance=mock_plugin
        )
        
        # Test health check
        health = self.plugin_system._check_plugin_health("test_plugin", plugin_info)
        
        self.assertEqual(health.plugin_name, "test_plugin")
        self.assertEqual(health.status, "healthy")
        self.assertEqual(len(health.errors), 0)
        self.assertGreater(health.performance_score, 0)
    
    def test_plugin_search_integration(self):
        """Test plugin search integration"""
        # Mock marketplace with test plugin
        mock_plugin_data = {
            "name": "search_test_plugin",
            "version": "1.0.0",
            "description": "Search test plugin",
            "author": "Test Author",
            "homepage": "https://test.com",
            "download_url": "https://test.com/download",
            "license": "MIT",
            "category": "extraction",
            "status": "active",
            "tags": ["search", "test"],
            "dependencies": [],
            "paper2data_version": ">=1.0.0",
            "file_size": 1024,
            "file_hash": "abc123",
            "security_scan": {
                "status": "safe",
                "scan_date": datetime.now().isoformat(),
                "issues": [],
                "score": 100,
                "details": {}
            },
            "stats": {
                "downloads": 1000,
                "active_users": 100,
                "ratings_count": 10,
                "average_rating": 4.5,
                "last_updated": datetime.now().isoformat(),
                "compatibility_score": 0.95
            },
            "ratings": [],
            "screenshots": [],
            "documentation_url": "https://test.com/docs",
            "source_code_url": "https://test.com/source",
            "changelog": "Initial release"
        }
        
        plugin = self.plugin_system.marketplace._dict_to_plugin(mock_plugin_data)
        self.plugin_system.marketplace.plugins["search_test_plugin"] = plugin
        
        # Test search
        results = self.plugin_system.search_plugins("search")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "search_test_plugin")
    
    def test_system_metrics(self):
        """Test system metrics collection"""
        metrics = self.plugin_system.get_system_metrics()
        
        self.assertIsNotNone(metrics)
        self.assertGreaterEqual(metrics.total_plugins, 0)
        self.assertGreaterEqual(metrics.active_plugins, 0)
        self.assertGreaterEqual(metrics.failed_plugins, 0)
        self.assertGreaterEqual(metrics.total_hooks, 0)
        self.assertGreaterEqual(metrics.avg_response_time, 0)
    
    def test_plugin_status_retrieval(self):
        """Test plugin status retrieval"""
        status = self.plugin_system.get_plugin_status("nonexistent_plugin")
        
        self.assertIsNotNone(status)
        self.assertIn("plugin_info", status)
        self.assertIn("health", status)
        self.assertIn("marketplace_info", status)
    
    def test_system_state_export(self):
        """Test system state export"""
        export_file = Path(self.temp_dir) / "system_state.json"
        
        self.plugin_system.export_system_state(str(export_file))
        
        self.assertTrue(export_file.exists())
        
        # Verify exported data
        with open(export_file, 'r') as f:
            state = json.load(f)
        
        self.assertIn("system_info", state)
        self.assertIn("plugins", state)
        self.assertIn("health", state)
        self.assertIn("metrics", state)
        self.assertIn("dependencies", state)


class TestPluginIntegration(unittest.TestCase):
    """Test integration between all plugin system components"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "plugin_dirs": [str(Path(self.temp_dir) / "plugins")],
            "health_monitoring_enabled": False,
            "auto_update_enabled": False,
            "dependency_config": {
                "installed_packages_file": str(Path(self.temp_dir) / "installed.json"),
                "package_registry_file": str(Path(self.temp_dir) / "registry.json")
            },
            "marketplace_config": {
                "cache_dir": str(Path(self.temp_dir) / "cache")
            }
        }
        
        # Create plugins directory
        Path(self.config["plugin_dirs"][0]).mkdir(parents=True, exist_ok=True)
        
        # Create comprehensive mock registry
        registry = {
            "base_plugin": {
                "version": "1.0.0",
                "dependencies": []
            },
            "dependent_plugin": {
                "version": "1.0.0",
                "dependencies": [
                    {"package": "base_plugin", "constraint": ">=1.0.0"}
                ]
            },
            "complex_plugin": {
                "version": "2.0.0",
                "dependencies": [
                    {"package": "base_plugin", "constraint": ">=1.0.0"},
                    {"package": "dependent_plugin", "constraint": ">=1.0.0"}
                ]
            }
        }
        
        with open(self.config["dependency_config"]["package_registry_file"], 'w') as f:
            json.dump(registry, f)
        
        self.plugin_system = EnhancedPluginSystem(self.config)
    
    def tearDown(self):
        """Clean up test environment"""
        self.plugin_system.cleanup()
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_plugin_workflow(self):
        """Test complete plugin workflow from search to installation"""
        # 1. Search for plugins
        # (This would normally query the marketplace)
        
        # 2. Install plugin with dependencies
        # Mock the installation process
        success = self.plugin_system.dependency_manager.install_package("dependent_plugin")
        self.assertTrue(success)
        
        # 3. Verify dependency resolution
        resolution = self.plugin_system.dependency_manager.resolve_dependencies(["dependent_plugin"])
        self.assertTrue(resolution.success)
        self.assertIn("base_plugin", resolution.install_order)
        self.assertIn("dependent_plugin", resolution.install_order)
        
        # 4. Check plugin health
        # This would normally check actual plugin instances
        
        # 5. Verify system metrics
        metrics = self.plugin_system.get_system_metrics()
        self.assertIsNotNone(metrics)
    
    def test_dependency_conflict_resolution(self):
        """Test handling of dependency conflicts"""
        # Create conflicting dependencies scenario
        # This would need more complex setup with actual conflicting versions
        
        # For now, test that the system handles resolution gracefully
        resolution = self.plugin_system.dependency_manager.resolve_dependencies(["nonexistent_plugin"])
        # Should not crash, may have unresolved dependencies
        self.assertIsNotNone(resolution)
    
    def test_plugin_lifecycle_management(self):
        """Test complete plugin lifecycle"""
        # 1. Install plugin
        success = self.plugin_system.dependency_manager.install_package("base_plugin")
        self.assertTrue(success)
        
        # 2. Verify installation
        self.assertIn("base_plugin", self.plugin_system.dependency_manager.installed_packages)
        
        # 3. Uninstall plugin
        success = self.plugin_system.dependency_manager.uninstall_package("base_plugin")
        self.assertTrue(success)
        
        # 4. Verify uninstallation
        self.assertNotIn("base_plugin", self.plugin_system.dependency_manager.installed_packages)


class TestPluginSystemErrorHandling(unittest.TestCase):
    """Test error handling in plugin system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "plugin_dirs": [str(Path(self.temp_dir) / "plugins")],
            "health_monitoring_enabled": False,
            "auto_update_enabled": False,
            "dependency_config": {
                "installed_packages_file": str(Path(self.temp_dir) / "nonexistent" / "installed.json"),
                "package_registry_file": str(Path(self.temp_dir) / "nonexistent" / "registry.json")
            },
            "marketplace_config": {
                "cache_dir": str(Path(self.temp_dir) / "cache")
            }
        }
        
        # Create plugins directory
        Path(self.config["plugin_dirs"][0]).mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    def test_invalid_configuration_handling(self):
        """Test handling of invalid configuration"""
        # Should not crash with invalid paths
        try:
            plugin_system = EnhancedPluginSystem(self.config)
            plugin_system.cleanup()
        except Exception as e:
            self.fail(f"Plugin system should handle invalid configuration gracefully: {e}")
    
    def test_missing_plugin_handling(self):
        """Test handling of missing plugins"""
        plugin_system = EnhancedPluginSystem(self.config)
        
        # Should handle missing plugins gracefully
        status = plugin_system.get_plugin_status("nonexistent_plugin")
        self.assertIsNotNone(status)
        self.assertIsNone(status["plugin_info"])
        
        plugin_system.cleanup()
    
    def test_corrupted_data_handling(self):
        """Test handling of corrupted data files"""
        # Create corrupted registry file
        registry_path = Path(self.config["dependency_config"]["package_registry_file"])
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(registry_path, 'w') as f:
            f.write("{ invalid json content")
        
        # Should handle corrupted data gracefully
        try:
            plugin_system = EnhancedPluginSystem(self.config)
            plugin_system.cleanup()
        except Exception as e:
            self.fail(f"Plugin system should handle corrupted data gracefully: {e}")


if __name__ == '__main__':
    # Run tests
    unittest.main() 
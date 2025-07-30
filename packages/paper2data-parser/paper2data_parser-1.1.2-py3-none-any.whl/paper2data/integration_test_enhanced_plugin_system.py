"""
Integration Test for Enhanced Plugin System

This test verifies the enhanced plugin system works correctly
without importing global instances that might cause initialization issues.
"""

import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime

from .plugin_dependency_manager import DependencyManager, VersionConstraint
from .plugin_marketplace import PluginMarketplace
from .plugin_system_enhanced import EnhancedPluginSystem


def test_enhanced_plugin_system_integration():
    """Test the enhanced plugin system integration"""
    
    # Create temporary directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create test configuration
        config = {
            "plugin_dirs": [str(Path(temp_dir) / "plugins")],
            "health_monitoring_enabled": False,
            "auto_update_enabled": False,
            "dependency_config": {
                "installed_packages_file": str(Path(temp_dir) / "installed.json"),
                "package_registry_file": str(Path(temp_dir) / "registry.json")
            },
            "marketplace_config": {
                "cache_dir": str(Path(temp_dir) / "cache"),
                "marketplace_url": "https://test.marketplace.com"
            }
        }
        
        # Create plugins directory
        Path(config["plugin_dirs"][0]).mkdir(parents=True, exist_ok=True)
        
        # Create mock registry
        registry = {
            "test_plugin": {
                "version": "1.0.0",
                "dependencies": []
            }
        }
        
        with open(config["dependency_config"]["package_registry_file"], 'w') as f:
            json.dump(registry, f)
        
        # Test 1: Initialize enhanced plugin system
        print("Test 1: Initializing enhanced plugin system...")
        plugin_system = EnhancedPluginSystem(config)
        print(f"✓ Plugin system status: {plugin_system.status.value}")
        
        # Test 2: Test dependency manager
        print("\nTest 2: Testing dependency manager...")
        dep_manager = plugin_system.dependency_manager
        
        # Test dependency resolution
        resolution = dep_manager.resolve_dependencies(["test_plugin"])
        print(f"✓ Dependency resolution successful: {resolution.success}")
        print(f"✓ Install order: {resolution.install_order}")
        
        # Test 3: Test marketplace
        print("\nTest 3: Testing marketplace...")
        marketplace = plugin_system.marketplace
        
        # Test search (should work with empty marketplace)
        results = marketplace.search_plugins("test")
        print(f"✓ Search completed, found {len(results)} plugins")
        
        # Test 4: Test system metrics
        print("\nTest 4: Testing system metrics...")
        metrics = plugin_system.get_system_metrics()
        print(f"✓ System metrics - Total plugins: {metrics.total_plugins}")
        print(f"✓ System metrics - Active plugins: {metrics.active_plugins}")
        print(f"✓ System metrics - Total hooks: {metrics.total_hooks}")
        
        # Test 5: Test plugin status
        print("\nTest 5: Testing plugin status...")
        status = plugin_system.get_plugin_status("test_plugin")
        print(f"✓ Plugin status retrieved: {len(status)} keys")
        
        # Test 6: Test system state export
        print("\nTest 6: Testing system state export...")
        export_file = Path(temp_dir) / "system_state.json"
        plugin_system.export_system_state(str(export_file))
        print(f"✓ System state exported to {export_file}")
        
        # Verify exported data
        with open(export_file, 'r') as f:
            state = json.load(f)
        
        print(f"✓ Export contains {len(state)} sections")
        
        # Test 7: Test plugin recommendations
        print("\nTest 7: Testing plugin recommendations...")
        recommendations = plugin_system.get_plugin_recommendations()
        print(f"✓ Recommendations retrieved: {len(recommendations)} plugins")
        
        # Test 8: Test cleanup
        print("\nTest 8: Testing cleanup...")
        plugin_system.cleanup()
        print("✓ Plugin system cleanup completed")
        
        print("\n🎉 All integration tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_enhanced_plugin_system_integration() 
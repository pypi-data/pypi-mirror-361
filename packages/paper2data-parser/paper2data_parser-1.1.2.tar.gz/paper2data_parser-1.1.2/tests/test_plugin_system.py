"""
Test suite for Paper2Data Plugin System

This test suite validates the plugin architecture, including:
- Plugin loading and management
- Hook registration and execution
- Plugin configuration and validation
- Integration with the main processing pipeline
- Error handling and plugin lifecycle management

Author: Paper2Data Team
Version: 1.0.0
"""

import pytest
import os
import tempfile
import json
from typing import Dict, List, Any, Optional
from unittest.mock import MagicMock, patch

from paper2data.plugin_manager import (
    PluginManager, BasePlugin, PluginMetadata, PluginInfo, PluginStatus,
    HookPriority, plugin_hook, get_plugin_manager, initialize_plugin_system
)
from paper2data.plugin_hooks import (
    HookCategory, execute_hook, execute_hook_until_success, register_hook,
    get_hook_definition, validate_hook_name, ALL_HOOKS
)


class TestPlugin(BasePlugin):
    """Test plugin for validation"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.setup_called = False
        self.cleanup_called = False
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin for unit tests",
            author="Test Author",
            license="MIT",
            dependencies=[],
            hooks=["test_hook", "process_equations"],
            config_schema={
                "type": "object",
                "properties": {
                    "test_param": {
                        "type": "string",
                        "default": "test_value"
                    }
                }
            }
        )
    
    def setup(self) -> bool:
        self.setup_called = True
        return True
    
    def cleanup(self) -> bool:
        self.cleanup_called = True
        return True
    
    @plugin_hook("test_hook", HookPriority.HIGH, "Test hook for validation")
    def test_hook_handler(self, data: str) -> str:
        return f"processed: {data}"
    
    @plugin_hook("process_equations", HookPriority.NORMAL, "Process equations")
    def process_equations_handler(self, equations: List[Dict[str, Any]], 
                                 config: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Add test enhancement to equations
        enhanced_equations = []
        for eq in equations:
            enhanced_eq = eq.copy()
            enhanced_eq["enhanced_by_plugin"] = True
            enhanced_equations.append(enhanced_eq)
        return enhanced_equations


class TestPluginManager:
    """Test cases for PluginManager"""
    
    @pytest.fixture
    def plugin_manager(self):
        """Create a fresh plugin manager for each test"""
        return PluginManager()
    
    @pytest.fixture
    def test_plugin_file(self):
        """Create a temporary plugin file for testing"""
        plugin_code = '''
from paper2data.plugin_manager import BasePlugin, PluginMetadata, plugin_hook

class TempTestPlugin(BasePlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="temp_test_plugin",
            version="1.0.0",
            description="Temporary test plugin",
            author="Test",
            hooks=["test_hook"]
        )
    
    def setup(self):
        return True
    
    def cleanup(self):
        return True
    
    @plugin_hook("test_hook")
    def test_handler(self, data):
        return f"temp_processed: {data}"

plugin_instance = TempTestPlugin
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_plugin.py', delete=False) as f:
            f.write(plugin_code)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        if os.path.exists(temp_file):
            os.unlink(temp_file)
    
    def test_plugin_manager_initialization(self, plugin_manager):
        """Test plugin manager initialization"""
        assert plugin_manager.plugins == {}
        assert plugin_manager.hooks == {}
        assert plugin_manager.plugin_config == {}
        assert plugin_manager.load_order == []
    
    def test_plugin_directory_management(self, plugin_manager):
        """Test plugin directory management"""
        test_dir = "/test/plugin/dir"
        plugin_manager.add_plugin_directory(test_dir)
        assert test_dir in plugin_manager.plugin_dirs
        
        # Adding duplicate should not create duplicates
        plugin_manager.add_plugin_directory(test_dir)
        assert plugin_manager.plugin_dirs.count(test_dir) == 1
    
    def test_plugin_loading_from_file(self, plugin_manager, test_plugin_file):
        """Test loading plugin from file"""
        plugin_info = plugin_manager.load_plugin_from_file(test_plugin_file)
        
        assert plugin_info is not None
        assert plugin_info.metadata.name == "temp_test_plugin"
        assert plugin_info.status == PluginStatus.LOADED
        assert plugin_info.instance is not None
        assert plugin_info.load_time is not None
        
        # Check if plugin is registered
        assert "temp_test_plugin" in plugin_manager.plugins
        
        # Check if hooks are registered
        assert "test_hook" in plugin_manager.hooks
    
    def test_plugin_loading_error_handling(self, plugin_manager):
        """Test error handling during plugin loading"""
        # Test with non-existent file
        plugin_info = plugin_manager.load_plugin_from_file("/non/existent/file.py")
        assert plugin_info is not None
        assert plugin_info.status == PluginStatus.ERROR
        assert plugin_info.error_message is not None
    
    def test_plugin_unloading(self, plugin_manager):
        """Test plugin unloading"""
        # Create and load a test plugin
        plugin_info = PluginInfo(
            metadata=PluginMetadata(
                name="test_unload",
                version="1.0.0",
                description="Test unload",
                author="Test"
            ),
            status=PluginStatus.LOADED,
            file_path="test.py",
            instance=TestPlugin()
        )
        
        plugin_manager.plugins["test_unload"] = plugin_info
        
        # Test unloading
        result = plugin_manager.unload_plugin("test_unload")
        assert result is True
        assert "test_unload" not in plugin_manager.plugins
        assert plugin_info.instance.cleanup_called is True
    
    def test_plugin_enable_disable(self, plugin_manager):
        """Test plugin enable/disable functionality"""
        # Create test plugin
        test_plugin = TestPlugin()
        plugin_info = PluginInfo(
            metadata=test_plugin.get_metadata(),
            status=PluginStatus.LOADED,
            file_path="test.py",
            instance=test_plugin
        )
        
        plugin_manager.plugins["test_plugin"] = plugin_info
        
        # Test enabling
        result = plugin_manager.enable_plugin("test_plugin")
        assert result is True
        assert plugin_info.status == PluginStatus.ENABLED
        
        # Test disabling
        result = plugin_manager.disable_plugin("test_plugin")
        assert result is True
        assert plugin_info.status == PluginStatus.DISABLED
    
    def test_plugin_configuration(self, plugin_manager):
        """Test plugin configuration"""
        # Create test plugin
        test_plugin = TestPlugin()
        plugin_info = PluginInfo(
            metadata=test_plugin.get_metadata(),
            status=PluginStatus.LOADED,
            file_path="test.py",
            instance=test_plugin
        )
        
        plugin_manager.plugins["test_plugin"] = plugin_info
        
        # Test configuration
        config = {"test_param": "new_value"}
        result = plugin_manager.configure_plugin("test_plugin", config)
        assert result is True
        assert plugin_info.config["test_param"] == "new_value"
        assert test_plugin.config["test_param"] == "new_value"
    
    def test_hook_execution(self, plugin_manager):
        """Test hook execution"""
        # Create test plugin with hooks
        test_plugin = TestPlugin()
        plugin_info = PluginInfo(
            metadata=test_plugin.get_metadata(),
            status=PluginStatus.LOADED,
            file_path="test.py",
            instance=test_plugin
        )
        
        plugin_manager.plugins["test_plugin"] = plugin_info
        plugin_manager._register_plugin_hooks(plugin_info)
        
        # Test hook execution
        results = plugin_manager.execute_hook("test_hook", "test_data")
        assert len(results) == 1
        assert results[0] == "processed: test_data"
    
    def test_hook_execution_until_success(self, plugin_manager):
        """Test hook execution until success"""
        # Create test plugin with hooks
        test_plugin = TestPlugin()
        plugin_info = PluginInfo(
            metadata=test_plugin.get_metadata(),
            status=PluginStatus.LOADED,
            file_path="test.py",
            instance=test_plugin
        )
        
        plugin_manager.plugins["test_plugin"] = plugin_info
        plugin_manager._register_plugin_hooks(plugin_info)
        
        # Test hook execution until success
        result = plugin_manager.execute_hook_until_success("test_hook", "test_data")
        assert result == "processed: test_data"
    
    def test_plugin_statistics(self, plugin_manager):
        """Test plugin statistics"""
        # Create test plugin
        test_plugin = TestPlugin()
        plugin_info = PluginInfo(
            metadata=test_plugin.get_metadata(),
            status=PluginStatus.LOADED,
            file_path="test.py",
            instance=test_plugin,
            execution_count=5,
            total_execution_time=1.5
        )
        
        plugin_manager.plugins["test_plugin"] = plugin_info
        
        # Get statistics
        stats = plugin_manager.get_plugin_statistics()
        assert "test_plugin" in stats
        assert stats["test_plugin"]["execution_count"] == 5
        assert stats["test_plugin"]["total_execution_time"] == 1.5
        assert stats["test_plugin"]["average_execution_time"] == 0.3
    
    def test_configuration_export(self, plugin_manager):
        """Test configuration export"""
        # Create test plugin
        test_plugin = TestPlugin()
        plugin_info = PluginInfo(
            metadata=test_plugin.get_metadata(),
            status=PluginStatus.LOADED,
            file_path="test.py",
            instance=test_plugin
        )
        
        plugin_manager.plugins["test_plugin"] = plugin_info
        
        # Export configuration
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            plugin_manager.export_configuration(temp_file)
            
            # Verify export
            with open(temp_file, 'r') as f:
                config = json.load(f)
            
            assert "plugins" in config
            assert "plugin_info" in config
            assert "test_plugin" in config["plugin_info"]
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestPluginHooks:
    """Test cases for plugin hooks"""
    
    def test_hook_validation(self):
        """Test hook name validation"""
        # Test valid hooks
        assert validate_hook_name("process_equations") is True
        assert validate_hook_name("extract_text") is True
        assert validate_hook_name("validate_output") is True
        
        # Test invalid hooks
        assert validate_hook_name("invalid_hook") is False
        assert validate_hook_name("") is False
        assert validate_hook_name(None) is False
    
    def test_hook_definition_retrieval(self):
        """Test hook definition retrieval"""
        hook_def = get_hook_definition("process_equations")
        assert hook_def is not None
        assert hook_def.name == "process_equations"
        assert hook_def.category == HookCategory.ANALYSIS
        
        # Test non-existent hook
        hook_def = get_hook_definition("non_existent_hook")
        assert hook_def is None
    
    def test_hook_categories(self):
        """Test hook categories"""
        assert HookCategory.DOCUMENT in [cat for cat in HookCategory]
        assert HookCategory.CONTENT in [cat for cat in HookCategory]
        assert HookCategory.ANALYSIS in [cat for cat in HookCategory]
        assert HookCategory.OUTPUT in [cat for cat in HookCategory]
        assert HookCategory.SYSTEM in [cat for cat in HookCategory]
    
    def test_global_hook_registry(self):
        """Test global hook registry"""
        # Test that all hooks are registered
        assert len(ALL_HOOKS) > 0
        
        # Test specific hooks
        assert "process_equations" in ALL_HOOKS
        assert "extract_text" in ALL_HOOKS
        assert "detect_sections" in ALL_HOOKS
        assert "validate_output" in ALL_HOOKS
        
        # Test hook definitions
        for hook_name, hook_def in ALL_HOOKS.items():
            assert hook_def.name == hook_name
            assert hook_def.category in [cat for cat in HookCategory]
            assert hook_def.description
            assert hook_def.parameters
            assert hook_def.return_type


class TestPluginIntegration:
    """Test cases for plugin integration with main processing"""
    
    @pytest.fixture
    def sample_pdf_content(self):
        """Create sample PDF content for testing"""
        # This would normally be actual PDF bytes
        # For testing, we'll use a mock
        return b"mock_pdf_content"
    
    def test_plugin_system_initialization(self):
        """Test plugin system initialization"""
        # Test global plugin manager
        manager = get_plugin_manager()
        assert isinstance(manager, PluginManager)
        
        # Test initialization with parameters
        manager = initialize_plugin_system(
            plugin_dirs=["/test/plugins"],
            config_file=None
        )
        assert isinstance(manager, PluginManager)
        assert "/test/plugins" in manager.plugin_dirs
    
    @patch('paper2data.plugin_manager.get_plugin_manager')
    def test_hook_execution_integration(self, mock_get_manager):
        """Test hook execution through global interface"""
        # Mock plugin manager
        mock_manager = MagicMock()
        mock_manager.execute_hook.return_value = ["test_result"]
        mock_get_manager.return_value = mock_manager
        
        # Test hook execution
        results = execute_hook("test_hook", "test_data")
        assert results == ["test_result"]
        mock_manager.execute_hook.assert_called_once_with("test_hook", "test_data")
    
    @patch('paper2data.plugin_manager.get_plugin_manager')
    def test_hook_execution_until_success_integration(self, mock_get_manager):
        """Test hook execution until success through global interface"""
        # Mock plugin manager
        mock_manager = MagicMock()
        mock_manager.execute_hook_until_success.return_value = "success_result"
        mock_get_manager.return_value = mock_manager
        
        # Test hook execution until success
        result = execute_hook_until_success("test_hook", "test_data")
        assert result == "success_result"
        mock_manager.execute_hook_until_success.assert_called_once_with("test_hook", "test_data")
    
    def test_plugin_decorator(self):
        """Test plugin hook decorator"""
        class TestDecoratorPlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="decorator_test",
                    version="1.0.0",
                    description="Test decorator",
                    author="Test"
                )
            
            def setup(self):
                return True
            
            def cleanup(self):
                return True
            
            @plugin_hook("test_hook", HookPriority.HIGH, "Test decorator hook")
            def decorated_handler(self, data):
                return f"decorated: {data}"
        
        # Test that the decorator adds the required attributes
        plugin = TestDecoratorPlugin()
        handler = plugin.decorated_handler
        
        assert hasattr(handler, '_plugin_hook_name')
        assert hasattr(handler, '_plugin_hook_priority')
        assert hasattr(handler, '_plugin_hook_description')
        
        assert handler._plugin_hook_name == "test_hook"
        assert handler._plugin_hook_priority == HookPriority.HIGH
        assert handler._plugin_hook_description == "Test decorator hook"


class TestPluginErrorHandling:
    """Test cases for plugin error handling"""
    
    def test_plugin_loading_with_invalid_syntax(self):
        """Test plugin loading with invalid Python syntax"""
        invalid_plugin_code = '''
import invalid syntax here
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_plugin.py', delete=False) as f:
            f.write(invalid_plugin_code)
            temp_file = f.name
        
        try:
            manager = PluginManager()
            plugin_info = manager.load_plugin_from_file(temp_file)
            
            assert plugin_info is not None
            assert plugin_info.status == PluginStatus.ERROR
            assert plugin_info.error_message is not None
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_plugin_loading_with_missing_base_class(self):
        """Test plugin loading with missing BasePlugin inheritance"""
        invalid_plugin_code = '''
class InvalidPlugin:
    pass

plugin_instance = InvalidPlugin
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_plugin.py', delete=False) as f:
            f.write(invalid_plugin_code)
            temp_file = f.name
        
        try:
            manager = PluginManager()
            plugin_info = manager.load_plugin_from_file(temp_file)
            
            assert plugin_info is not None
            assert plugin_info.status == PluginStatus.ERROR
            assert "No plugin class found" in plugin_info.error_message
            
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_hook_execution_with_exceptions(self):
        """Test hook execution with plugin exceptions"""
        class ErrorPlugin(BasePlugin):
            def get_metadata(self):
                return PluginMetadata(
                    name="error_plugin",
                    version="1.0.0",
                    description="Error plugin",
                    author="Test"
                )
            
            def setup(self):
                return True
            
            def cleanup(self):
                return True
            
            @plugin_hook("test_hook")
            def error_handler(self, data):
                raise ValueError("Test error")
        
        manager = PluginManager()
        plugin = ErrorPlugin()
        plugin_info = PluginInfo(
            metadata=plugin.get_metadata(),
            status=PluginStatus.LOADED,
            file_path="test.py",
            instance=plugin
        )
        
        manager.plugins["error_plugin"] = plugin_info
        manager._register_plugin_hooks(plugin_info)
        
        # Test that hook execution continues despite errors
        results = manager.execute_hook("test_hook", "test_data")
        assert results == []  # No successful results
        
        # Test that plugin status is updated
        assert plugin_info.status == PluginStatus.ERROR
        assert plugin_info.error_message is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
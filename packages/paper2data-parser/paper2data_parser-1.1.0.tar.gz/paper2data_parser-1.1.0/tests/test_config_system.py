"""
Comprehensive tests for the Paper2Data configuration system.

Tests configuration schema validation, smart defaults, and configuration management.
"""

import pytest
import tempfile
import yaml
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

from paper2data.config_schema import (
    Paper2DataConfig,
    CONFIG_PROFILES,
    OutputConfig,
    ProcessingConfig,
    LogLevel,
    OutputFormat
)
from paper2data.smart_defaults import (
    SmartDefaultsGenerator,
    get_smart_config,
    get_system_info,
    create_config_file,
    get_config_profiles
)
from paper2data.config_validator import (
    ConfigValidator,
    ValidationResult,
    validate_config,
    get_validation_report,
    fix_config_issues
)
from paper2data.config_manager import (
    ConfigManager,
    ConfigurationStatus,
    load_config,
    save_config,
    get_configuration_status
)


class TestConfigSchema:
    """Test configuration schema validation."""
    
    def test_default_config_creation(self):
        """Test creating config with all defaults."""
        config = Paper2DataConfig()
        
        assert config.output.format == OutputFormat.JSON
        assert config.output.directory == Path("./paper2data_output")
        assert config.processing.extract_figures is True
        assert config.processing.extract_tables is True
        assert config.logging.level == LogLevel.INFO
    
    def test_config_validation_valid(self):
        """Test valid configuration passes validation."""
        config_dict = {
            "output": {
                "format": "json",
                "directory": "./test_output"
            },
            "processing": {
                "extract_figures": True,
                "max_file_size_mb": 50
            },
            "logging": {
                "level": "DEBUG"
            }
        }
        
        config = Paper2DataConfig(**config_dict)
        assert config.output.format == OutputFormat.JSON
        assert config.processing.max_file_size_mb == 50
        assert config.logging.level == LogLevel.DEBUG
    
    def test_config_validation_invalid_enum(self):
        """Test invalid enum values raise validation error."""
        config_dict = {
            "output": {
                "format": "invalid_format"
            }
        }
        
        with pytest.raises(Exception):  # pydantic ValidationError
            Paper2DataConfig(**config_dict)
    
    def test_config_validation_invalid_range(self):
        """Test invalid range values raise validation error."""
        config_dict = {
            "processing": {
                "max_file_size_mb": 2000  # Too high
            }
        }
        
        with pytest.raises(Exception):  # pydantic ValidationError
            Paper2DataConfig(**config_dict)
    
    def test_config_validation_invalid_type(self):
        """Test invalid types raise validation error."""
        config_dict = {
            "processing": {
                "extract_figures": "yes"  # Should be bool
            }
        }
        
        with pytest.raises(Exception):  # pydantic ValidationError
            Paper2DataConfig(**config_dict)
    
    def test_config_profiles_valid(self):
        """Test all predefined profiles are valid."""
        for profile_name, profile_config in CONFIG_PROFILES.items():
            config = Paper2DataConfig(**profile_config)
            assert config is not None
    
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_system_dependent_validation(self, mock_memory, mock_cpu):
        """Test system-dependent validation."""
        # Mock system with 4 cores and 8GB RAM
        mock_cpu.return_value = 4
        mock_memory.return_value = MagicMock(total=8*1024*1024*1024)
        
        config_dict = {
            "processing": {
                "parallel_workers": 2,  # Should be valid
                "memory_limit_mb": 2048  # Should be valid
            }
        }
        
        config = Paper2DataConfig(**config_dict)
        assert config.processing.parallel_workers == 2


class TestSmartDefaults:
    """Test smart defaults generation."""
    
    def setUp(self):
        self.generator = SmartDefaultsGenerator()
    
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_system_assessment(self, mock_disk, mock_memory, mock_cpu):
        """Test system capabilities assessment."""
        mock_cpu.return_value = 8
        mock_memory.return_value = MagicMock(
            total=16*1024*1024*1024,
            available=12*1024*1024*1024
        )
        mock_disk.return_value = MagicMock(free=100*1024*1024*1024)
        
        generator = SmartDefaultsGenerator()
        caps = generator.system_caps
        
        assert caps.cpu_cores == 8
        assert caps.memory_total_mb == 16384
        assert caps.memory_available_mb == 12288
        assert caps.storage_available_gb == 100
    
    def test_balanced_config_generation(self):
        """Test balanced configuration generation."""
        config = get_smart_config(use_case="balanced")
        
        assert isinstance(config, Paper2DataConfig)
        assert config.processing.mode == "balanced"
        assert config.processing.extract_figures is True
        assert config.processing.extract_tables is True
    
    def test_fast_config_generation(self):
        """Test fast configuration generation."""
        config = get_smart_config(use_case="fast")
        
        assert isinstance(config, Paper2DataConfig)
        assert config.processing.mode == "fast"
        # Fast config should have lower quality settings
        assert config.tables.confidence_threshold <= 0.7
    
    def test_research_config_generation(self):
        """Test research configuration generation."""
        config = get_smart_config(use_case="research")
        
        assert isinstance(config, Paper2DataConfig)
        assert config.processing.mode == "thorough"
        assert config.processing.extract_equations is True
        assert config.plugins.enabled is True
    
    def test_system_info_generation(self):
        """Test system information generation."""
        info = get_system_info()
        
        assert "system_info" in info
        assert "recommendations" in info
        assert "warnings" in info
        assert "optimal_settings" in info
        
        assert "cpu_cores" in info["system_info"]
        assert "memory_gb" in info["system_info"]
    
    def test_config_profiles_list(self):
        """Test configuration profiles listing."""
        profiles = get_config_profiles()
        
        assert isinstance(profiles, dict)
        assert "fast" in profiles
        assert "balanced" in profiles
        assert "thorough" in profiles
        assert "research" in profiles
        
        for profile, description in profiles.items():
            assert isinstance(description, str)
            assert len(description) > 0
    
    def test_config_file_creation(self):
        """Test configuration file creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yml"
            
            create_config_file(config_path, use_case="balanced")
            
            assert config_path.exists()
            
            # Load and verify the created config
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            
            assert "output" in config_dict
            assert "processing" in config_dict
            assert "_metadata" in config_dict
    
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    def test_resource_constrained_config(self, mock_memory, mock_cpu):
        """Test configuration for resource-constrained systems."""
        # Mock low-end system
        mock_cpu.return_value = 2
        mock_memory.return_value = MagicMock(
            total=4*1024*1024*1024,
            available=2*1024*1024*1024
        )
        
        generator = SmartDefaultsGenerator()
        config = generator.generate_config(use_case="balanced")
        
        # Should have conservative settings
        assert config.processing.parallel_workers <= 4
        assert config.processing.memory_limit_mb <= 2048


class TestConfigValidator:
    """Test configuration validator."""
    
    def setUp(self):
        self.validator = ConfigValidator()
    
    def test_valid_config_validation(self):
        """Test validation of valid configuration."""
        config_dict = {
            "output": {
                "format": "json",
                "directory": "./test_output"
            },
            "processing": {
                "extract_figures": True,
                "max_file_size_mb": 50
            }
        }
        
        result = validate_config(config_dict)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_invalid_config_validation(self):
        """Test validation of invalid configuration."""
        config_dict = {
            "output": {
                "format": "invalid_format"
            },
            "processing": {
                "max_file_size_mb": 2000  # Too high
            }
        }
        
        result = validate_config(config_dict)
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.errors) > 0
    
    def test_config_file_validation(self):
        """Test validation of configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yml"
            
            config_dict = {
                "output": {"format": "json"},
                "processing": {"extract_figures": True}
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f)
            
            result = validate_config(config_path)
            assert result.is_valid is True
    
    def test_config_validation_with_warnings(self):
        """Test configuration validation with warnings."""
        config_dict = {
            "processing": {
                "max_file_size_mb": 300,  # Large but not invalid
                "timeout_seconds": 30     # Short timeout
            }
        }
        
        result = validate_config(config_dict)
        
        assert len(result.warnings) > 0
        assert len(result.suggestions) > 0
    
    def test_config_fix_issues(self):
        """Test automatic config issue fixing."""
        config_dict = {
            "processing": {
                "timeout_seconds": 30  # Too short
            }
        }
        
        result = validate_config(config_dict, fix_issues=True)
        
        if result.fixed_config:
            assert result.fixed_config["processing"]["timeout_seconds"] >= 60
    
    def test_validation_report_generation(self):
        """Test validation report generation."""
        config_dict = {
            "output": {"format": "invalid_format"}
        }
        
        report = get_validation_report(config_dict)
        
        assert isinstance(report, str)
        assert "Configuration Validation Report" in report
        assert "Errors:" in report
    
    @patch('pathlib.Path.exists')
    def test_nonexistent_config_file(self, mock_exists):
        """Test handling of nonexistent configuration file."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            validate_config("/nonexistent/config.yml")
    
    def test_profile_validation(self):
        """Test validation of predefined profiles."""
        validator = ConfigValidator()
        
        # Test valid profile
        result = validator.validate_profile("balanced")
        assert result.is_valid is True
        
        # Test invalid profile
        result = validator.validate_profile("nonexistent")
        assert result.is_valid is False
        assert len(result.errors) > 0


class TestConfigManager:
    """Test configuration manager."""
    
    def setUp(self):
        self.manager = ConfigManager()
    
    def test_config_loading_with_defaults(self):
        """Test configuration loading with smart defaults."""
        config = load_config(use_smart_defaults=True)
        
        assert isinstance(config, Paper2DataConfig)
        assert config.output.format in [OutputFormat.JSON, OutputFormat.YAML, OutputFormat.MARKDOWN]
    
    def test_config_loading_from_file(self):
        """Test configuration loading from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yml"
            
            config_dict = {
                "output": {"format": "yaml"},
                "processing": {"extract_figures": False}
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f)
            
            config = load_config(config_path=config_path)
            
            assert config.output.format == OutputFormat.YAML
            assert config.processing.extract_figures is False
    
    def test_config_loading_from_profile(self):
        """Test configuration loading from profile."""
        config = load_config(profile="fast")
        
        assert isinstance(config, Paper2DataConfig)
        assert config.processing.mode == "fast"
    
    def test_config_saving_yaml(self):
        """Test configuration saving in YAML format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.yml"
            
            config = Paper2DataConfig()
            save_config(config, config_path, format="yaml")
            
            assert config_path.exists()
            
            with open(config_path, 'r') as f:
                loaded_config = yaml.safe_load(f)
            
            assert "output" in loaded_config
            assert "processing" in loaded_config
    
    def test_config_saving_json(self):
        """Test configuration saving in JSON format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "test_config.json"
            
            config = Paper2DataConfig()
            save_config(config, config_path, format="json")
            
            assert config_path.exists()
            
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            assert "output" in loaded_config
            assert "processing" in loaded_config
    
    def test_configuration_status(self):
        """Test configuration status assessment."""
        status = get_configuration_status()
        
        assert isinstance(status, ConfigurationStatus)
        assert isinstance(status.has_config, bool)
        assert isinstance(status.is_valid, bool)
        assert isinstance(status.system_optimal, bool)
    
    def test_config_validation_with_system_check(self):
        """Test configuration validation with system compatibility check."""
        config_dict = {
            "processing": {
                "parallel_workers": 32,  # Likely too high for most systems
                "memory_limit_mb": 32768  # Very high memory limit
            }
        }
        
        result = validate_config(config_dict)
        
        # Should have warnings about system compatibility
        assert len(result.warnings) > 0
    
    def test_config_profile_application(self):
        """Test applying configuration profiles."""
        for profile_name in CONFIG_PROFILES.keys():
            config = load_config(profile=profile_name)
            
            assert isinstance(config, Paper2DataConfig)
            # Each profile should have valid settings
            assert config.processing.max_file_size_mb > 0
            assert config.processing.timeout_seconds > 0
    
    def test_config_merge_with_defaults(self):
        """Test configuration merging with smart defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "partial_config.yml"
            
            # Create partial configuration
            partial_config = {
                "output": {"format": "markdown"},
                "processing": {"extract_tables": False}
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(partial_config, f)
            
            config = load_config(config_path=config_path, use_smart_defaults=True)
            
            # Should have user settings
            assert config.output.format == OutputFormat.MARKDOWN
            assert config.processing.extract_tables is False
            
            # Should also have smart defaults for missing settings
            assert config.processing.parallel_workers > 0
            assert config.processing.memory_limit_mb > 0
    
    def test_invalid_config_handling(self):
        """Test handling of invalid configurations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "invalid_config.yml"
            
            # Create invalid configuration
            invalid_config = {
                "output": {"format": "invalid_format"},
                "processing": {"max_file_size_mb": -1}
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(invalid_config, f)
            
            with pytest.raises(ValueError):
                load_config(config_path=config_path, validate=True)
    
    def test_config_without_validation(self):
        """Test loading configuration without validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config_no_validation.yml"
            
            config_dict = {
                "output": {"format": "json"},
                "processing": {"extract_figures": True}
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f)
            
            # Should not raise exception even with validation disabled
            config = load_config(config_path=config_path, validate=False)
            assert isinstance(config, Paper2DataConfig)


class TestConfigIntegration:
    """Integration tests for the configuration system."""
    
    def test_end_to_end_config_workflow(self):
        """Test complete configuration workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "workflow_config.yml"
            
            # 1. Create config with smart defaults
            create_config_file(config_path, use_case="balanced")
            
            # 2. Load and validate
            config = load_config(config_path=config_path)
            assert isinstance(config, Paper2DataConfig)
            
            # 3. Validate explicitly
            result = validate_config(config_path)
            assert result.is_valid is True
            
            # 4. Modify and save
            config.processing.extract_equations = True
            save_config(config, config_path)
            
            # 5. Reload and verify
            reloaded_config = load_config(config_path=config_path)
            assert reloaded_config.processing.extract_equations is True
    
    def test_backwards_compatibility(self):
        """Test backwards compatibility with legacy configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "legacy_config.yml"
            
            # Create legacy-style configuration
            legacy_config = {
                "output": {
                    "format": "json",
                    "directory": "./output"
                },
                "processing": {
                    "extract_figures": True,
                    "extract_tables": True,
                    "max_file_size_mb": 100
                },
                "logging": {
                    "level": "INFO"
                }
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(legacy_config, f)
            
            # Should load successfully with new system
            config = load_config(config_path=config_path)
            assert isinstance(config, Paper2DataConfig)
            assert config.output.format == OutputFormat.JSON
            assert config.processing.extract_figures is True
    
    def test_error_recovery(self):
        """Test error recovery and fallback mechanisms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "corrupted_config.yml"
            
            # Create corrupted YAML
            with open(config_path, 'w') as f:
                f.write("invalid: yaml: content: [")
            
            # Should handle gracefully and provide fallback
            try:
                config = load_config(config_path=config_path, validate=False)
                # If it succeeds, it should be a valid config
                assert isinstance(config, Paper2DataConfig)
            except Exception as e:
                # If it fails, should provide meaningful error
                assert "configuration" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__]) 
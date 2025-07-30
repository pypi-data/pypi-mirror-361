"""
Configuration manager for Paper2Data.

This module provides the main interface for configuration management,
bringing together schema validation, smart defaults, and configuration
file handling.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass

from .config_schema import Paper2DataConfig, CONFIG_PROFILES
from .smart_defaults import (
    SmartDefaultsGenerator,
    smart_defaults,
    get_smart_config,
    get_system_info,
    create_config_file,
    get_config_profiles
)
from .config_validator import (
    ConfigValidator,
    ValidationResult,
    config_validator,
    validate_config,
    get_validation_report
)


@dataclass
class ConfigurationStatus:
    """Status of configuration system."""
    has_config: bool
    config_path: Optional[Path]
    is_valid: bool
    profile: Optional[str]
    errors: List[str]
    warnings: List[str]
    system_optimal: bool


class ConfigManager:
    """Comprehensive configuration manager."""
    
    def __init__(self):
        self.validator = ConfigValidator()
        self.smart_defaults = SmartDefaultsGenerator()
        self.default_config_paths = [
            Path.cwd() / "paper2data.yml",
            Path.cwd() / "paper2data.yaml",
            Path.cwd() / ".paper2data.yml",
            Path.cwd() / ".paper2data.yaml",
            Path.home() / ".paper2data" / "config.yml",
            Path.home() / ".paper2data" / "config.yaml",
            Path.home() / ".config" / "paper2data" / "config.yml",
            Path.home() / ".config" / "paper2data" / "config.yaml"
        ]
    
    def load_config(
        self,
        config_path: Optional[Union[Path, str]] = None,
        profile: Optional[str] = None,
        use_smart_defaults: bool = True,
        validate: bool = True
    ) -> Paper2DataConfig:
        """Load configuration with comprehensive handling."""
        
        # If specific config path provided, use it
        if config_path:
            config_dict = self._load_config_file(Path(config_path))
        # If profile specified, use profile
        elif profile:
            if profile not in CONFIG_PROFILES:
                raise ValueError(f"Unknown profile: {profile}")
            config_dict = CONFIG_PROFILES[profile].copy()
        else:
            # Search for configuration file
            config_dict = self._find_and_load_config()
        
        # Apply smart defaults if requested
        if use_smart_defaults:
            config_dict = self._apply_smart_defaults(config_dict)
        
        # Create configuration object
        try:
            config = Paper2DataConfig(**config_dict)
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")
        
        # Validate if requested
        if validate:
            validation_result = self.validator.validate_config(config)
            if not validation_result.is_valid:
                errors = "\n".join(validation_result.errors)
                raise ValueError(f"Configuration validation failed:\n{errors}")
        
        return config
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yml', '.yaml']:
                config_dict = yaml.safe_load(f) or {}
            elif config_path.suffix.lower() == '.json':
                config_dict = json.load(f) or {}
            else:
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
        
        # Filter out metadata fields that are not part of the schema
        filtered_config = {}
        valid_fields = {
            'output', 'processing', 'tables', 'figures', 'logging', 
            'api', 'plugins', 'version', 'profile'
        }
        
        for key, value in config_dict.items():
            if key in valid_fields:
                filtered_config[key] = value
        
        return filtered_config
    
    def _find_and_load_config(self) -> Dict[str, Any]:
        """Find and load configuration from default locations."""
        for config_path in self.default_config_paths:
            if config_path.exists():
                return self._load_config_file(config_path)
        
        # No configuration found, return empty dict for smart defaults
        return {}
    
    def _apply_smart_defaults(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Apply smart defaults to configuration."""
        # Determine use case from config or infer
        use_case = config_dict.get('profile', 'balanced')
        
        # Generate smart configuration
        smart_config = self.smart_defaults.generate_config(use_case=use_case)
        smart_dict = smart_config.dict(exclude_none=True)
        
        # Merge user config with smart defaults (user config takes precedence)
        merged_config = smart_dict.copy()
        self._deep_merge_dict(merged_config, config_dict)
        
        return merged_config
    
    def _deep_merge_dict(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge_dict(base[key], value)
            else:
                base[key] = value
    
    def save_config(
        self,
        config: Union[Paper2DataConfig, Dict[str, Any]],
        config_path: Union[Path, str],
        format: str = "yaml",
        include_metadata: bool = True
    ) -> None:
        """Save configuration to file."""
        
        # Convert to dictionary
        if isinstance(config, Paper2DataConfig):
            config_dict = config.dict(exclude_none=True)
        else:
            config_dict = config.copy()
        
        # Add metadata if requested
        if include_metadata:
            config_dict["_metadata"] = {
                "generated_by": "Paper2Data Configuration Manager",
                "version": "1.0.0",
                "system_info": get_system_info()["system_info"]
            }
        
        # Save to file
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if format.lower() in ['yml', 'yaml']:
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
            elif format.lower() == 'json':
                json.dump(config_dict, f, indent=2, sort_keys=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
    
    def create_config_interactive(self, config_path: Optional[Union[Path, str]] = None) -> Path:
        """Create configuration interactively."""
        import inquirer
        
        print("🔧 Paper2Data Configuration Setup")
        print("=" * 35)
        
        questions = [
            inquirer.List(
                'profile',
                message="Choose a configuration profile",
                choices=list(get_config_profiles().keys()),
                default='balanced'
            ),
            inquirer.List(
                'output_format',
                message="Default output format",
                choices=['json', 'yaml', 'markdown'],
                default='json'
            ),
            inquirer.Path(
                'output_directory',
                message="Default output directory",
                default='./paper2data_output',
                path_type=inquirer.Path.DIRECTORY
            ),
            inquirer.Confirm(
                'extract_figures',
                message="Extract figures by default?",
                default=True
            ),
            inquirer.Confirm(
                'extract_tables',
                message="Extract tables by default?",
                default=True
            ),
            inquirer.Confirm(
                'extract_citations',
                message="Extract citations by default?",
                default=True
            ),
            inquirer.List(
                'log_level',
                message="Default logging level",
                choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                default='INFO'
            ),
            inquirer.Confirm(
                'enable_api',
                message="Enable API integrations (arXiv, CrossRef)?",
                default=True
            ),
            inquirer.Confirm(
                'enable_plugins',
                message="Enable plugin system?",
                default=True
            )
        ]
        
        answers = inquirer.prompt(questions)
        
        # Create configuration based on answers
        profile = answers['profile']
        config = self.smart_defaults.create_config_for_use_case(profile)
        
        # Apply user preferences
        config.output.format = answers['output_format']
        config.output.directory = Path(answers['output_directory'])
        config.processing.extract_figures = answers['extract_figures']
        config.processing.extract_tables = answers['extract_tables']
        config.processing.extract_citations = answers['extract_citations']
        config.logging.level = answers['log_level']
        config.api.enable_arxiv = answers['enable_api']
        config.api.enable_crossref = answers['enable_api']
        config.plugins.enabled = answers['enable_plugins']
        
        # Determine config path
        if config_path is None:
            config_path = Path.cwd() / "paper2data.yml"
        else:
            config_path = Path(config_path)
        
        # Save configuration
        self.save_config(config, config_path)
        
        print(f"\n✅ Configuration saved to: {config_path}")
        print("🚀 Ready to process papers!")
        
        return config_path
    
    def validate_current_config(self) -> ValidationResult:
        """Validate current configuration."""
        try:
            config = self.load_config(validate=False)
            return self.validator.validate_config(config)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Failed to load configuration: {e}"],
                warnings=[],
                suggestions=["Check configuration file syntax and location"]
            )
    
    def get_configuration_status(self) -> ConfigurationStatus:
        """Get comprehensive configuration status."""
        
        # Find configuration file
        config_path = None
        for path in self.default_config_paths:
            if path.exists():
                config_path = path
                break
        
        has_config = config_path is not None
        
        # Validate configuration
        validation_result = self.validate_current_config()
        
        # Check if configuration is system-optimal
        system_info = get_system_info()
        system_optimal = len(system_info["warnings"]) == 0
        
        # Determine profile
        profile = None
        if has_config:
            try:
                config_dict = self._load_config_file(config_path)
                profile = config_dict.get('profile', 'custom')
            except Exception:
                pass
        
        return ConfigurationStatus(
            has_config=has_config,
            config_path=config_path,
            is_valid=validation_result.is_valid,
            profile=profile,
            errors=validation_result.errors,
            warnings=validation_result.warnings,
            system_optimal=system_optimal
        )
    
    def fix_configuration(self, config_path: Optional[Union[Path, str]] = None) -> bool:
        """Attempt to fix configuration issues."""
        
        if config_path:
            path = Path(config_path)
        else:
            # Find existing configuration
            path = None
            for p in self.default_config_paths:
                if p.exists():
                    path = p
                    break
        
        if not path:
            print("No configuration file found to fix")
            return False
        
        # Validate and fix
        validation_result = self.validator.validate_config(path, fix_issues=True)
        
        if validation_result.fixed_config:
            # Backup original
            backup_path = path.with_suffix(path.suffix + '.backup')
            path.rename(backup_path)
            
            # Save fixed configuration
            self.save_config(validation_result.fixed_config, path)
            
            print(f"✅ Configuration fixed and saved to: {path}")
            print(f"💾 Original backed up to: {backup_path}")
            return True
        else:
            print("❌ No automatic fixes available")
            return False
    
    def get_config_help(self) -> str:
        """Get comprehensive configuration help."""
        
        help_text = []
        help_text.append("Paper2Data Configuration Help")
        help_text.append("=" * 30)
        help_text.append("")
        
        # Available profiles
        help_text.append("Available Profiles:")
        help_text.append("-" * 18)
        for profile, description in get_config_profiles().items():
            help_text.append(f"  {profile}: {description}")
        help_text.append("")
        
        # Configuration locations
        help_text.append("Configuration File Locations (in order of precedence):")
        help_text.append("-" * 55)
        for i, path in enumerate(self.default_config_paths, 1):
            help_text.append(f"  {i}. {path}")
        help_text.append("")
        
        # System information
        system_info = get_system_info()
        help_text.append("System Information:")
        help_text.append("-" * 18)
        help_text.append(f"  CPU Cores: {system_info['system_info']['cpu_cores']}")
        help_text.append(f"  Memory: {system_info['system_info']['memory_gb']:.1f} GB")
        help_text.append(f"  Storage: {system_info['system_info']['storage_gb']:.1f} GB")
        help_text.append(f"  Platform: {system_info['system_info']['platform']}")
        help_text.append("")
        
        # Recommendations
        if system_info['recommendations']:
            help_text.append("System Recommendations:")
            help_text.append("-" * 22)
            for rec in system_info['recommendations']:
                help_text.append(f"  • {rec}")
            help_text.append("")
        
        # Warnings
        if system_info['warnings']:
            help_text.append("System Warnings:")
            help_text.append("-" * 16)
            for warning in system_info['warnings']:
                help_text.append(f"  ⚠️  {warning}")
            help_text.append("")
        
        return "\n".join(help_text)


# Global configuration manager
config_manager = ConfigManager()


def load_config(
    config_path: Optional[Union[Path, str]] = None,
    profile: Optional[str] = None,
    use_smart_defaults: bool = True,
    validate: bool = True
) -> Paper2DataConfig:
    """Load configuration with comprehensive handling."""
    return config_manager.load_config(
        config_path=config_path,
        profile=profile,
        use_smart_defaults=use_smart_defaults,
        validate=validate
    )


def save_config(
    config: Union[Paper2DataConfig, Dict[str, Any]],
    config_path: Union[Path, str],
    format: str = "yaml"
) -> None:
    """Save configuration to file."""
    config_manager.save_config(config, config_path, format)


def create_config_interactive(config_path: Optional[Union[Path, str]] = None) -> Path:
    """Create configuration interactively."""
    return config_manager.create_config_interactive(config_path)


def get_configuration_status() -> ConfigurationStatus:
    """Get comprehensive configuration status."""
    return config_manager.get_configuration_status()


def fix_configuration(config_path: Optional[Union[Path, str]] = None) -> bool:
    """Attempt to fix configuration issues."""
    return config_manager.fix_configuration(config_path)


def get_config_help() -> str:
    """Get comprehensive configuration help."""
    return config_manager.get_config_help() 
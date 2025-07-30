"""
Configuration validator for Paper2Data.

This module provides comprehensive validation for configuration files,
including schema validation, value range checking, dependency validation,
and detailed error reporting.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from pydantic import ValidationError as PydanticValidationError
from .config_schema import Paper2DataConfig, CONFIG_PROFILES
from .smart_defaults import smart_defaults


@dataclass
class ValidationResult:
    """Result of configuration validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    fixed_config: Optional[Dict[str, Any]] = None


@dataclass
class ConfigValidationError:
    """Configuration validation error."""
    field: str
    message: str
    severity: str  # error, warning, info
    suggested_fix: Optional[str] = None


class ConfigValidator:
    """Comprehensive configuration validator."""
    
    def __init__(self):
        self.system_info = smart_defaults.get_system_recommendations()
    
    def validate_config(
        self,
        config: Union[Dict[str, Any], Paper2DataConfig, Path, str],
        fix_issues: bool = False
    ) -> ValidationResult:
        """Validate configuration comprehensively."""
        
        # Convert input to dictionary
        if isinstance(config, (Path, str)):
            config_dict = self._load_config_file(config)
        elif isinstance(config, Paper2DataConfig):
            config_dict = config.model_dump(exclude_none=True)
        else:
            config_dict = config.copy()
        
        errors = []
        warnings = []
        suggestions = []
        
        # Schema validation
        schema_result = self._validate_schema(config_dict)
        errors.extend(schema_result.errors)
        warnings.extend(schema_result.warnings)
        suggestions.extend(schema_result.suggestions)
        
        # Value validation
        value_result = self._validate_values(config_dict)
        errors.extend(value_result.errors)
        warnings.extend(value_result.warnings)
        suggestions.extend(value_result.suggestions)
        
        # Dependency validation
        dependency_result = self._validate_dependencies(config_dict)
        errors.extend(dependency_result.errors)
        warnings.extend(dependency_result.warnings)
        suggestions.extend(dependency_result.suggestions)
        
        # System compatibility validation
        system_result = self._validate_system_compatibility(config_dict)
        errors.extend(system_result.errors)
        warnings.extend(system_result.warnings)
        suggestions.extend(system_result.suggestions)
        
        # Performance validation
        performance_result = self._validate_performance(config_dict)
        errors.extend(performance_result.errors)
        warnings.extend(performance_result.warnings)
        suggestions.extend(performance_result.suggestions)
        
        # Try to fix issues if requested
        fixed_config = None
        if fix_issues and (errors or warnings):
            fixed_config = self._fix_config_issues(config_dict, errors + warnings)
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            fixed_config=fixed_config
        )
    
    def _load_config_file(self, config_path: Union[Path, str]) -> Dict[str, Any]:
        """Load configuration from file."""
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yml', '.yaml']:
                config_dict = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                import json
                config_dict = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {path.suffix}")
        
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
    
    def _validate_schema(self, config_dict: Dict[str, Any]) -> ValidationResult:
        """Validate configuration against schema."""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # Try to create Paper2DataConfig instance
            Paper2DataConfig(**config_dict)
        except PydanticValidationError as e:
            for error in e.errors():
                field = '.'.join(str(x) for x in error['loc'])
                message = error['msg']
                
                errors.append(f"Schema validation failed for '{field}': {message}")
                
                # Add suggestions for common errors
                if 'required' in message.lower():
                    suggestions.append(f"Add required field '{field}' to configuration")
                elif 'extra' in message.lower():
                    suggestions.append(f"Remove unknown field '{field}' from configuration")
                elif 'type' in message.lower():
                    suggestions.append(f"Check type of field '{field}' - {message}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _validate_values(self, config_dict: Dict[str, Any]) -> ValidationResult:
        """Validate configuration values."""
        errors = []
        warnings = []
        suggestions = []
        
        # Validate processing configuration
        if 'processing' in config_dict:
            processing = config_dict['processing']
            
            # Check file size limits
            max_file_size = processing.get('max_file_size_mb', 100)
            if max_file_size > 500:
                warnings.append(f"Large max_file_size_mb ({max_file_size}MB) may cause memory issues")
                suggestions.append("Consider reducing max_file_size_mb for better stability")
            
            # Check timeout settings
            timeout = processing.get('timeout_seconds', 300)
            if timeout < 60:
                warnings.append(f"Short timeout ({timeout}s) may cause processing failures")
                suggestions.append("Consider increasing timeout_seconds to at least 60")
            elif timeout > 3600:
                warnings.append(f"Long timeout ({timeout}s) may cause hanging processes")
                suggestions.append("Consider reducing timeout_seconds to under 1 hour")
            
            # Check parallel workers
            workers = processing.get('parallel_workers', 0)
            if workers > 16:
                warnings.append(f"High parallel_workers ({workers}) may overwhelm system")
                suggestions.append("Consider reducing parallel_workers for better stability")
        
        # Validate output configuration
        if 'output' in config_dict:
            output = config_dict['output']
            
            # Check output directory
            output_dir = output.get('directory', './paper2data_output')
            try:
                path = Path(output_dir)
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
                # Test write permissions
                test_file = path / '.write_test'
                test_file.touch()
                test_file.unlink()
            except Exception as e:
                errors.append(f"Output directory not writable: {e}")
                suggestions.append("Check output directory permissions or choose different location")
        
        # Validate logging configuration
        if 'logging' in config_dict:
            logging = config_dict['logging']
            
            # Check log file
            log_file = logging.get('file')
            if log_file:
                try:
                    log_path = Path(log_file)
                    log_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Test write permissions
                    if log_path.exists():
                        if not os.access(log_path, os.W_OK):
                            errors.append(f"Log file not writable: {log_path}")
                    else:
                        test_file = log_path.parent / '.write_test'
                        test_file.touch()
                        test_file.unlink()
                except Exception as e:
                    errors.append(f"Log file path invalid: {e}")
                    suggestions.append("Check log file path or choose different location")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _validate_dependencies(self, config_dict: Dict[str, Any]) -> ValidationResult:
        """Validate configuration dependencies."""
        errors = []
        warnings = []
        suggestions = []
        
        # Check equation processing dependencies
        processing = config_dict.get('processing', {})
        if processing.get('extract_equations', False):
            plugins = config_dict.get('plugins', {})
            if not plugins.get('enabled', True):
                errors.append("Equation extraction requires plugin system to be enabled")
                suggestions.append("Set plugins.enabled = true for equation extraction")
        
        # Check figure analysis dependencies
        figures = config_dict.get('figures', {})
        if figures.get('analyze_content', False):
            plugins = config_dict.get('plugins', {})
            if not plugins.get('enabled', True):
                warnings.append("Figure analysis requires plugin system for best results")
                suggestions.append("Enable plugins for advanced figure analysis")
        
        # Check API dependencies
        api = config_dict.get('api', {})
        if api.get('cache_enabled', True):
            cache_ttl = api.get('cache_ttl_hours', 24)
            if cache_ttl < 1:
                warnings.append("Very short cache TTL may cause excessive API calls")
                suggestions.append("Consider cache_ttl_hours of at least 1 hour")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _validate_system_compatibility(self, config_dict: Dict[str, Any]) -> ValidationResult:
        """Validate configuration against system capabilities."""
        errors = []
        warnings = []
        suggestions = []
        
        system_info = self.system_info["system_info"]
        
        # Check memory requirements
        processing = config_dict.get('processing', {})
        memory_limit = processing.get('memory_limit_mb', 0)
        
        if memory_limit > 0:
            available_memory = system_info["memory_mb"] * 1024
            if memory_limit > available_memory * 0.8:
                warnings.append(f"Memory limit ({memory_limit}MB) may exceed available memory")
                suggestions.append(f"Consider reducing memory_limit_mb to {int(available_memory * 0.6)}MB")
        
        # Check CPU requirements
        workers = processing.get('parallel_workers', 0)
        if workers > 0:
            cpu_cores = system_info["cpu_cores"]
            if workers > cpu_cores * 2:
                warnings.append(f"Parallel workers ({workers}) significantly exceed CPU cores ({cpu_cores})")
                suggestions.append(f"Consider reducing parallel_workers to {cpu_cores}")
        
        # Check storage requirements
        storage_gb = system_info["storage_gb"]
        if storage_gb < 5:
            warnings.append(f"Low storage space ({storage_gb}GB) may cause processing failures")
            suggestions.append("Free up disk space before processing large files")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _validate_performance(self, config_dict: Dict[str, Any]) -> ValidationResult:
        """Validate configuration for performance issues."""
        errors = []
        warnings = []
        suggestions = []
        
        # Check for performance anti-patterns
        processing = config_dict.get('processing', {})
        
        # Single worker with large files
        workers = processing.get('parallel_workers', 1)
        max_file_size = processing.get('max_file_size_mb', 100)
        
        if workers == 1 and max_file_size > 50:
            warnings.append("Single worker with large files may be slow")
            suggestions.append("Consider enabling parallel processing for large files")
        
        # High quality settings with many workers
        figures = config_dict.get('figures', {})
        if (figures.get('quality', 95) == 100 and 
            figures.get('analyze_content', False) and 
            workers > 4):
            warnings.append("High quality figure processing with many workers may cause memory issues")
            suggestions.append("Consider reducing parallel_workers or figure quality")
        
        # No caching with API usage
        api = config_dict.get('api', {})
        if (api.get('enable_arxiv', True) or api.get('enable_crossref', True)):
            if not api.get('cache_enabled', True):
                warnings.append("API usage without caching may be slow and hit rate limits")
                suggestions.append("Enable API caching for better performance")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
    
    def _fix_config_issues(
        self, 
        config_dict: Dict[str, Any], 
        issues: List[str]
    ) -> Dict[str, Any]:
        """Attempt to fix configuration issues automatically."""
        fixed_config = config_dict.copy()
        
        # Fix common issues
        for issue in issues:
            if "memory_limit_mb" in issue.lower() and "exceed" in issue.lower():
                # Fix memory limit
                recommended_memory = int(self.system_info["system_info"]["memory_mb"] * 1024 * 0.6)
                if 'processing' not in fixed_config:
                    fixed_config['processing'] = {}
                fixed_config['processing']['memory_limit_mb'] = recommended_memory
            
            elif "parallel_workers" in issue.lower() and "exceed" in issue.lower():
                # Fix parallel workers
                recommended_workers = self.system_info["system_info"]["cpu_cores"]
                if 'processing' not in fixed_config:
                    fixed_config['processing'] = {}
                fixed_config['processing']['parallel_workers'] = recommended_workers
            
            elif "timeout" in issue.lower() and "short" in issue.lower():
                # Fix short timeout
                if 'processing' not in fixed_config:
                    fixed_config['processing'] = {}
                fixed_config['processing']['timeout_seconds'] = 300
            
            elif "cache" in issue.lower() and "enable" in issue.lower():
                # Enable caching
                if 'api' not in fixed_config:
                    fixed_config['api'] = {}
                fixed_config['api']['cache_enabled'] = True
        
        return fixed_config
    
    def validate_config_file(self, config_path: Union[Path, str]) -> ValidationResult:
        """Validate a configuration file."""
        return self.validate_config(config_path)
    
    def validate_profile(self, profile_name: str) -> ValidationResult:
        """Validate a configuration profile."""
        if profile_name not in CONFIG_PROFILES:
            return ValidationResult(
                is_valid=False,
                errors=[f"Unknown profile: {profile_name}"],
                warnings=[],
                suggestions=[f"Available profiles: {', '.join(CONFIG_PROFILES.keys())}"]
            )
        
        profile_config = CONFIG_PROFILES[profile_name]
        return self.validate_config(profile_config)
    
    def get_validation_report(self, config: Union[Dict[str, Any], Path, str]) -> str:
        """Get a formatted validation report."""
        result = self.validate_config(config)
        
        report = ["Configuration Validation Report", "=" * 35, ""]
        
        if result.is_valid:
            report.append("✅ Configuration is valid!")
        else:
            report.append("❌ Configuration has issues:")
        
        if result.errors:
            report.extend(["", "Errors:", "-------"])
            for i, error in enumerate(result.errors, 1):
                report.append(f"{i}. {error}")
        
        if result.warnings:
            report.extend(["", "Warnings:", "---------"])
            for i, warning in enumerate(result.warnings, 1):
                report.append(f"{i}. {warning}")
        
        if result.suggestions:
            report.extend(["", "Suggestions:", "------------"])
            for i, suggestion in enumerate(result.suggestions, 1):
                report.append(f"{i}. {suggestion}")
        
        return "\n".join(report)


# Global validator instance
config_validator = ConfigValidator()


def validate_config(config: Union[Dict[str, Any], Path, str]) -> ValidationResult:
    """Validate configuration."""
    return config_validator.validate_config(config)


def validate_config_file(config_path: Union[Path, str]) -> ValidationResult:
    """Validate configuration file."""
    return config_validator.validate_config_file(config_path)


def get_validation_report(config: Union[Dict[str, Any], Path, str]) -> str:
    """Get formatted validation report."""
    return config_validator.get_validation_report(config)


def fix_config_issues(config: Union[Dict[str, Any], Path, str]) -> Dict[str, Any]:
    """Attempt to fix configuration issues automatically."""
    result = config_validator.validate_config(config, fix_issues=True)
    return result.fixed_config or {} 
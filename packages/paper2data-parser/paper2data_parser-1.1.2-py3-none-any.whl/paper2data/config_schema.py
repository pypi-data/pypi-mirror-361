"""
Configuration schema definition with validation rules for Paper2Data.

This module defines the comprehensive configuration schema using pydantic
for type validation, value constraints, and automatic documentation.
"""

import os
import psutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class LogLevel(str, Enum):
    """Valid logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class OutputFormat(str, Enum):
    """Valid output formats."""
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"
    CSV = "csv"


class TableOutputFormat(str, Enum):
    """Valid table output formats."""
    CSV = "csv"
    JSON = "json"
    MARKDOWN = "markdown"
    EXCEL = "excel"


class ProcessingMode(str, Enum):
    """Processing mode options."""
    FAST = "fast"
    BALANCED = "balanced"
    THOROUGH = "thorough"
    CUSTOM = "custom"


class OutputConfig(BaseModel):
    """Output configuration settings."""
    format: OutputFormat = Field(
        default=OutputFormat.JSON,
        description="Primary output format for metadata"
    )
    directory: Path = Field(
        default=Path("./paper2data_output"),
        description="Base output directory for extracted content"
    )
    preserve_structure: bool = Field(
        default=True,
        description="Preserve original document structure in output"
    )
    create_readme: bool = Field(
        default=True,
        description="Generate README.md files for navigation"
    )
    organize_by_type: bool = Field(
        default=True,
        description="Organize output by content type (sections, figures, tables)"
    )
    include_raw_text: bool = Field(
        default=False,
        description="Include raw extracted text in output"
    )

    @field_validator('directory')
    @classmethod
    def validate_directory(cls, v):
        """Validate output directory is writable."""
        path = Path(v)
        try:
            path.mkdir(parents=True, exist_ok=True)
            # Test write permissions
            test_file = path / ".write_test"
            test_file.touch()
            test_file.unlink()
            return path
        except (OSError, PermissionError) as e:
            raise ValueError(f"Output directory not writable: {e}")


class ProcessingConfig(BaseModel):
    """Processing configuration settings."""
    mode: ProcessingMode = Field(
        default=ProcessingMode.BALANCED,
        description="Processing mode affecting speed vs accuracy tradeoff"
    )
    extract_figures: bool = Field(
        default=True,
        description="Extract figures and images from document"
    )
    extract_tables: bool = Field(
        default=True,
        description="Extract tables from document"
    )
    extract_citations: bool = Field(
        default=True,
        description="Extract citations and references"
    )
    extract_equations: bool = Field(
        default=False,
        description="Extract mathematical equations (requires additional dependencies)"
    )
    max_file_size_mb: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum file size in MB to process"
    )
    parallel_workers: int = Field(
        default=0,  # 0 means auto-detect
        ge=0,
        le=32,
        description="Number of parallel workers (0 for auto-detect)"
    )
    memory_limit_mb: int = Field(
        default=0,  # 0 means auto-detect
        ge=0,
        le=32768,
        description="Memory limit in MB (0 for auto-detect)"
    )
    timeout_seconds: int = Field(
        default=300,
        ge=30,
        le=3600,
        description="Processing timeout in seconds"
    )
    
    @field_validator('parallel_workers')
    @classmethod
    def validate_parallel_workers(cls, v):
        """Validate parallel workers against system capabilities."""
        if v == 0:
            # Auto-detect: use CPU count but cap at 8
            return min(psutil.cpu_count(logical=False) or 4, 8)
        
        max_workers = psutil.cpu_count(logical=False) or 4
        if v > max_workers:
            raise ValueError(f"Parallel workers ({v}) exceeds system CPU cores ({max_workers})")
        return v
    
    @field_validator('memory_limit_mb')
    @classmethod
    def validate_memory_limit(cls, v):
        """Validate memory limit against system memory."""
        if v == 0:
            # Auto-detect: use 50% of available memory
            available_mb = psutil.virtual_memory().available // (1024 * 1024)
            return min(int(available_mb * 0.5), 4096)  # Cap at 4GB
        
        available_mb = psutil.virtual_memory().available // (1024 * 1024)
        if v > available_mb:
            raise ValueError(f"Memory limit ({v}MB) exceeds available memory ({available_mb}MB)")
        return v


class TableConfig(BaseModel):
    """Table extraction configuration."""
    output_format: TableOutputFormat = Field(
        default=TableOutputFormat.CSV,
        description="Output format for extracted tables"
    )
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for table detection"
    )
    max_false_positives: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="Maximum acceptable false positive rate"
    )
    detect_headers: bool = Field(
        default=True,
        description="Attempt to detect table headers"
    )
    merge_cells: bool = Field(
        default=True,
        description="Handle merged cells in tables"
    )
    min_rows: int = Field(
        default=2,
        ge=1,
        le=100,
        description="Minimum number of rows to consider as table"
    )
    min_columns: int = Field(
        default=2,
        ge=1,
        le=50,
        description="Minimum number of columns to consider as table"
    )


class FigureConfig(BaseModel):
    """Figure extraction configuration."""
    output_format: Literal["png", "jpg", "svg", "pdf"] = Field(
        default="png",
        description="Output format for extracted figures"
    )
    min_width: int = Field(
        default=100,
        ge=50,
        le=5000,
        description="Minimum figure width in pixels"
    )
    min_height: int = Field(
        default=100,
        ge=50,
        le=5000,
        description="Minimum figure height in pixels"
    )
    extract_captions: bool = Field(
        default=True,
        description="Extract figure captions"
    )
    analyze_content: bool = Field(
        default=False,
        description="Analyze figure content (requires additional dependencies)"
    )
    quality: int = Field(
        default=95,
        ge=10,
        le=100,
        description="Output quality for compressed formats (1-100)"
    )


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level"
    )
    file: Optional[Path] = Field(
        default=None,
        description="Log file path (None for console only)"
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    max_file_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum log file size in MB"
    )
    backup_count: int = Field(
        default=5,
        ge=0,
        le=50,
        description="Number of backup log files to keep"
    )
    
    @field_validator('file')
    @classmethod
    def validate_log_file(cls, v):
        """Validate log file path is writable."""
        if v is None:
            return v
        
        path = Path(v)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            # Test write permissions
            if path.exists():
                # Check if file is writable
                if not os.access(path, os.W_OK):
                    raise ValueError(f"Log file not writable: {path}")
            else:
                # Test if directory is writable
                test_file = path.parent / ".write_test"
                test_file.touch()
                test_file.unlink()
            return path
        except (OSError, PermissionError) as e:
            raise ValueError(f"Log file path not accessible: {e}")


class APIConfig(BaseModel):
    """API integration configuration."""
    enable_arxiv: bool = Field(
        default=True,
        description="Enable arXiv API integration"
    )
    enable_crossref: bool = Field(
        default=True,
        description="Enable CrossRef API integration"
    )
    rate_limit_requests_per_second: float = Field(
        default=1.0,
        ge=0.1,
        le=100.0,
        description="API rate limit in requests per second"
    )
    timeout_seconds: int = Field(
        default=30,
        ge=5,
        le=300,
        description="API request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of API request retries"
    )
    cache_enabled: bool = Field(
        default=True,
        description="Enable API response caching"
    )
    cache_ttl_hours: int = Field(
        default=24,
        ge=1,
        le=168,  # 7 days
        description="Cache time-to-live in hours"
    )


class PluginConfig(BaseModel):
    """Plugin system configuration."""
    enabled: bool = Field(
        default=True,
        description="Enable plugin system"
    )
    plugin_directories: List[Path] = Field(
        default_factory=lambda: [Path("~/.paper2data/plugins").expanduser()],
        description="Directories to search for plugins"
    )
    auto_load: bool = Field(
        default=True,
        description="Automatically load available plugins"
    )
    enabled_plugins: List[str] = Field(
        default_factory=list,
        description="List of explicitly enabled plugins"
    )
    disabled_plugins: List[str] = Field(
        default_factory=list,
        description="List of explicitly disabled plugins"
    )


class Paper2DataConfig(BaseModel):
    """Complete Paper2Data configuration schema."""
    
    # Core configuration sections
    output: OutputConfig = Field(default_factory=OutputConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    tables: TableConfig = Field(default_factory=TableConfig)
    figures: FigureConfig = Field(default_factory=FigureConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    
    # Global settings
    version: str = Field(
        default="1.0.0",
        description="Configuration version"
    )
    profile: str = Field(
        default="default",
        description="Configuration profile name"
    )
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        extra = "forbid"  # Prevent unknown fields
        json_schema_extra = {
            "examples": [
                {
                    "output": {
                        "format": "json",
                        "directory": "./paper2data_output",
                        "preserve_structure": True
                    },
                    "processing": {
                        "mode": "balanced",
                        "extract_figures": True,
                        "extract_tables": True,
                        "extract_citations": True,
                        "max_file_size_mb": 100
                    },
                    "logging": {
                        "level": "INFO",
                        "file": None
                    }
                }
            ]
        }
    
    @model_validator(mode='after')
    def validate_config_consistency(self):
        """Validate configuration consistency across sections."""
        # Check if table extraction is enabled but table config is minimal
        if self.processing.extract_tables and not hasattr(self, 'tables'):
            self.tables = TableConfig()
        
        # Check if figure extraction is enabled but figure config is minimal
        if self.processing.extract_figures and not hasattr(self, 'figures'):
            self.figures = FigureConfig()
        
        # Validate memory limits against processing requirements
        memory_limit = self.processing.memory_limit_mb
        max_file_size = self.processing.max_file_size_mb
        
        if memory_limit > 0 and memory_limit < max_file_size * 2:
            raise ValueError(
                f"Memory limit ({memory_limit}MB) should be at least 2x max file size ({max_file_size}MB)"
            )
        
        return self
    
    def get_effective_config(self) -> Dict[str, Any]:
        """Get the effective configuration with all defaults applied."""
        return self.model_dump(exclude_none=True)
    
    def get_processing_recommendations(self) -> Dict[str, str]:
        """Get processing recommendations based on current configuration."""
        recommendations = []
        
        # Check system resources
        cpu_count = psutil.cpu_count(logical=False) or 4
        memory_mb = psutil.virtual_memory().total // (1024 * 1024)
        
        if self.processing.parallel_workers > cpu_count:
            recommendations.append(
                f"Consider reducing parallel_workers to {cpu_count} (CPU cores)"
            )
        
        if self.processing.memory_limit_mb > memory_mb * 0.8:
            recommendations.append(
                f"Consider reducing memory_limit_mb to {int(memory_mb * 0.8)}MB (80% of system memory)"
            )
        
        if self.processing.extract_equations and not self.plugins.enabled:
            recommendations.append(
                "Enable plugin system for equation extraction functionality"
            )
        
        return {
            "recommendations": recommendations,
            "system_info": {
                "cpu_cores": cpu_count,
                "memory_mb": memory_mb,
                "optimal_workers": min(cpu_count, 8),
                "recommended_memory_mb": min(int(memory_mb * 0.5), 4096)
            }
        }


# Pre-defined configuration profiles
CONFIG_PROFILES = {
    "fast": {
        "processing": {
            "mode": "fast",
            "extract_figures": True,
            "extract_tables": True,
            "extract_citations": False,
            "extract_equations": False,
            "parallel_workers": 0,  # Auto-detect
            "timeout_seconds": 120
        },
        "tables": {
            "confidence_threshold": 0.5,
            "detect_headers": False
        },
        "figures": {
            "extract_captions": False,
            "analyze_content": False
        }
    },
    "balanced": {
        "processing": {
            "mode": "balanced",
            "extract_figures": True,
            "extract_tables": True,
            "extract_citations": True,
            "extract_equations": False,
            "parallel_workers": 0,  # Auto-detect
            "timeout_seconds": 300
        },
        "tables": {
            "confidence_threshold": 0.7,
            "detect_headers": True
        },
        "figures": {
            "extract_captions": True,
            "analyze_content": False
        }
    },
    "thorough": {
        "processing": {
            "mode": "thorough",
            "extract_figures": True,
            "extract_tables": True,
            "extract_citations": True,
            "extract_equations": True,
            "parallel_workers": 0,  # Auto-detect
            "timeout_seconds": 600
        },
        "tables": {
            "confidence_threshold": 0.8,
            "detect_headers": True,
            "merge_cells": True
        },
        "figures": {
            "extract_captions": True,
            "analyze_content": True
        },
        "plugins": {
            "enabled": True,
            "auto_load": True
        }
    },
    "research": {
        "processing": {
            "mode": "thorough",
            "extract_figures": True,
            "extract_tables": True,
            "extract_citations": True,
            "extract_equations": True,
            "parallel_workers": 0,  # Auto-detect
            "timeout_seconds": 900
        },
        "tables": {
            "confidence_threshold": 0.9,
            "output_format": "csv",
            "detect_headers": True,
            "merge_cells": True
        },
        "figures": {
            "extract_captions": True,
            "analyze_content": True,
            "quality": 100
        },
        "output": {
            "format": "json",
            "create_readme": True,
            "organize_by_type": True,
            "include_raw_text": True
        },
        "api": {
            "enable_arxiv": True,
            "enable_crossref": True,
            "cache_enabled": True,
            "cache_ttl_hours": 168  # 7 days
        },
        "plugins": {
            "enabled": True,
            "auto_load": True
        }
    }
} 
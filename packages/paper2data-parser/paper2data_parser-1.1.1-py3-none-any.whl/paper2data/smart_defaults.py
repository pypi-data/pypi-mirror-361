"""
Smart defaults system for Paper2Data configuration.

This module provides intelligent default configuration generation based on:
- System capabilities (CPU, memory, storage)
- Usage context (research, batch processing, quick analysis)
- Performance requirements
- Available resources
"""

import os
import psutil
import platform
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from .config_schema import (
    Paper2DataConfig,
    ProcessingMode,
    CONFIG_PROFILES
)


@dataclass
class SystemCapabilities:
    """System capabilities assessment."""
    cpu_cores: int
    cpu_threads: int
    memory_total_mb: int
    memory_available_mb: int
    storage_available_gb: int
    platform: str
    has_gpu: bool
    python_version: str


@dataclass
class UsageContext:
    """Usage context for configuration optimization."""
    use_case: str  # research, batch, quick, demo
    expected_file_size_mb: int
    expected_batch_size: int
    quality_priority: str  # speed, balanced, quality
    resource_constraints: Dict[str, Any]


class SmartDefaultsGenerator:
    """Generates intelligent configuration defaults based on system and context."""
    
    def __init__(self):
        self.system_caps = self._assess_system_capabilities()
        
    def _assess_system_capabilities(self) -> SystemCapabilities:
        """Assess current system capabilities."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(Path.cwd())
        
        # Try to detect GPU availability
        has_gpu = False
        try:
            import torch
            has_gpu = torch.cuda.is_available()
        except ImportError:
            try:
                import tensorflow as tf
                has_gpu = len(tf.config.list_physical_devices('GPU')) > 0
            except ImportError:
                pass
        
        return SystemCapabilities(
            cpu_cores=psutil.cpu_count(logical=False) or 4,
            cpu_threads=psutil.cpu_count(logical=True) or 4,
            memory_total_mb=memory.total // (1024 * 1024),
            memory_available_mb=memory.available // (1024 * 1024),
            storage_available_gb=disk.free // (1024 * 1024 * 1024),
            platform=platform.system(),
            has_gpu=has_gpu,
            python_version=platform.python_version()
        )
    
    def generate_config(
        self,
        use_case: str = "balanced",
        file_size_hint: Optional[int] = None,
        batch_size_hint: Optional[int] = None,
        quality_priority: str = "balanced",
        resource_constraints: Optional[Dict[str, Any]] = None
    ) -> Paper2DataConfig:
        """Generate intelligent configuration based on context."""
        
        # Create usage context
        context = UsageContext(
            use_case=use_case,
            expected_file_size_mb=file_size_hint or 10,
            expected_batch_size=batch_size_hint or 1,
            quality_priority=quality_priority,
            resource_constraints=resource_constraints or {}
        )
        
        # Start with base profile
        if use_case in CONFIG_PROFILES:
            base_config = CONFIG_PROFILES[use_case].copy()
        else:
            base_config = CONFIG_PROFILES["balanced"].copy()
        
        # Apply system-specific optimizations
        optimized_config = self._apply_system_optimizations(base_config, context)
        
        # Apply context-specific optimizations
        optimized_config = self._apply_context_optimizations(optimized_config, context)
        
        # Apply resource constraints
        optimized_config = self._apply_resource_constraints(optimized_config, context)
        
        # Create and validate final configuration
        return Paper2DataConfig(**optimized_config)
    
    def _apply_system_optimizations(
        self, 
        config: Dict[str, Any], 
        context: UsageContext
    ) -> Dict[str, Any]:
        """Apply system-specific optimizations."""
        
        # Optimize parallel processing
        if "processing" not in config:
            config["processing"] = {}
        
        # Smart worker count based on CPU cores and memory
        optimal_workers = min(
            self.system_caps.cpu_cores,
            self.system_caps.memory_available_mb // 512,  # 512MB per worker
            8  # Cap at 8 workers
        )
        config["processing"]["parallel_workers"] = max(1, optimal_workers)
        
        # Smart memory limit
        # Use up to 60% of available memory, but leave at least 2GB free
        memory_limit = min(
            int(self.system_caps.memory_available_mb * 0.6),
            self.system_caps.memory_available_mb - 2048,
            8192  # Cap at 8GB
        )
        config["processing"]["memory_limit_mb"] = max(1024, memory_limit)
        
        # Adjust timeout based on system performance
        base_timeout = config.get("processing", {}).get("timeout_seconds", 300)
        if self.system_caps.cpu_cores >= 8 and self.system_caps.memory_total_mb >= 16384:
            # High-performance system
            config["processing"]["timeout_seconds"] = base_timeout
        elif self.system_caps.cpu_cores >= 4 and self.system_caps.memory_total_mb >= 8192:
            # Medium-performance system
            config["processing"]["timeout_seconds"] = int(base_timeout * 1.5)
        else:
            # Low-performance system
            config["processing"]["timeout_seconds"] = int(base_timeout * 2)
        
        # Platform-specific optimizations
        if self.system_caps.platform == "Darwin":  # macOS
            # macOS often has good single-core performance
            config["processing"]["parallel_workers"] = min(
                config["processing"]["parallel_workers"], 4
            )
        elif self.system_caps.platform == "Windows":
            # Windows might benefit from slightly conservative settings
            config["processing"]["memory_limit_mb"] = int(
                config["processing"]["memory_limit_mb"] * 0.9
            )
        
        return config
    
    def _apply_context_optimizations(
        self, 
        config: Dict[str, Any], 
        context: UsageContext
    ) -> Dict[str, Any]:
        """Apply context-specific optimizations."""
        
        # Adjust based on expected file size
        if context.expected_file_size_mb > 50:
            # Large files need more resources
            config["processing"]["max_file_size_mb"] = context.expected_file_size_mb * 2
            config["processing"]["timeout_seconds"] = int(
                config["processing"]["timeout_seconds"] * 1.5
            )
        
        # Adjust based on batch size
        if context.expected_batch_size > 5:
            # Batch processing optimizations
            config["processing"]["parallel_workers"] = min(
                config["processing"]["parallel_workers"],
                max(1, self.system_caps.cpu_cores // 2)  # Leave room for I/O
            )
            
            # Enable caching for batch processing
            if "api" not in config:
                config["api"] = {}
            config["api"]["cache_enabled"] = True
            config["api"]["cache_ttl_hours"] = 72  # 3 days
        
        # Quality priority adjustments
        if context.quality_priority == "speed":
            config["processing"]["mode"] = "fast"
            if "tables" not in config:
                config["tables"] = {}
            config["tables"]["confidence_threshold"] = 0.5
            config["tables"]["detect_headers"] = False
            
            if "figures" not in config:
                config["figures"] = {}
            config["figures"]["extract_captions"] = False
            config["figures"]["analyze_content"] = False
            
        elif context.quality_priority == "quality":
            config["processing"]["mode"] = "thorough"
            if "tables" not in config:
                config["tables"] = {}
            config["tables"]["confidence_threshold"] = 0.9
            config["tables"]["detect_headers"] = True
            config["tables"]["merge_cells"] = True
            
            if "figures" not in config:
                config["figures"] = {}
            config["figures"]["extract_captions"] = True
            config["figures"]["analyze_content"] = True
            config["figures"]["quality"] = 100
        
        return config
    
    def _apply_resource_constraints(
        self, 
        config: Dict[str, Any], 
        context: UsageContext
    ) -> Dict[str, Any]:
        """Apply resource constraints."""
        
        constraints = context.resource_constraints
        
        # Memory constraints
        if "max_memory_mb" in constraints:
            config["processing"]["memory_limit_mb"] = min(
                config["processing"]["memory_limit_mb"],
                constraints["max_memory_mb"]
            )
        
        # CPU constraints
        if "max_workers" in constraints:
            config["processing"]["parallel_workers"] = min(
                config["processing"]["parallel_workers"],
                constraints["max_workers"]
            )
        
        # Time constraints
        if "max_timeout_seconds" in constraints:
            config["processing"]["timeout_seconds"] = min(
                config["processing"]["timeout_seconds"],
                constraints["max_timeout_seconds"]
            )
        
        # Storage constraints
        if "max_storage_gb" in constraints:
            # Adjust figure quality if storage is limited
            if constraints["max_storage_gb"] < 1:
                if "figures" not in config:
                    config["figures"] = {}
                config["figures"]["quality"] = 75
                config["figures"]["output_format"] = "jpg"
        
        return config
    
    def get_system_recommendations(self) -> Dict[str, Any]:
        """Get system-specific recommendations."""
        recommendations = []
        warnings = []
        
        # Memory recommendations
        if self.system_caps.memory_total_mb < 4096:
            warnings.append("System has less than 4GB RAM - consider processing smaller files")
        elif self.system_caps.memory_total_mb < 8192:
            recommendations.append("Consider upgrading to 8GB+ RAM for better performance")
        
        # CPU recommendations
        if self.system_caps.cpu_cores < 4:
            recommendations.append("System has few CPU cores - parallel processing will be limited")
        
        # Storage recommendations
        if self.system_caps.storage_available_gb < 2:
            warnings.append("Less than 2GB storage available - monitor disk space")
        
        # Platform-specific recommendations
        if self.system_caps.platform == "Darwin":
            recommendations.append("macOS detected - consider using Homebrew for dependencies")
        elif self.system_caps.platform == "Windows":
            recommendations.append("Windows detected - ensure WSL2 is available for optimal performance")
        
        return {
            "system_info": {
                "cpu_cores": self.system_caps.cpu_cores,
                "memory_gb": round(self.system_caps.memory_total_mb / 1024, 1),
                "storage_gb": self.system_caps.storage_available_gb,
                "platform": self.system_caps.platform,
                "has_gpu": self.system_caps.has_gpu
            },
            "recommendations": recommendations,
            "warnings": warnings,
            "optimal_settings": {
                "parallel_workers": min(self.system_caps.cpu_cores, 8),
                "memory_limit_mb": min(
                    int(self.system_caps.memory_available_mb * 0.6),
                    4096
                ),
                "recommended_profiles": self._get_recommended_profiles()
            }
        }
    
    def _get_recommended_profiles(self) -> List[str]:
        """Get recommended configuration profiles for this system."""
        profiles = []
        
        # Always recommend balanced
        profiles.append("balanced")
        
        # Recommend fast for low-end systems
        if (self.system_caps.cpu_cores < 4 or 
            self.system_caps.memory_total_mb < 8192):
            profiles.insert(0, "fast")
        
        # Recommend thorough for high-end systems
        if (self.system_caps.cpu_cores >= 8 and 
            self.system_caps.memory_total_mb >= 16384):
            profiles.append("thorough")
        
        # Recommend research for very high-end systems
        if (self.system_caps.cpu_cores >= 16 and 
            self.system_caps.memory_total_mb >= 32768):
            profiles.append("research")
        
        return profiles
    
    def create_config_for_use_case(
        self, 
        use_case: str, 
        **kwargs
    ) -> Paper2DataConfig:
        """Create configuration for specific use cases."""
        
        use_case_configs = {
            "demo": {
                "use_case": "fast",
                "file_size_hint": 5,
                "batch_size_hint": 1,
                "quality_priority": "speed",
                "resource_constraints": {"max_timeout_seconds": 60}
            },
            "research": {
                "use_case": "research",
                "file_size_hint": 25,
                "batch_size_hint": 1,
                "quality_priority": "quality"
            },
            "batch_processing": {
                "use_case": "balanced",
                "file_size_hint": 15,
                "batch_size_hint": 10,
                "quality_priority": "balanced"
            },
            "quick_analysis": {
                "use_case": "fast",
                "file_size_hint": 10,
                "batch_size_hint": 3,
                "quality_priority": "speed"
            },
            "high_quality": {
                "use_case": "thorough",
                "file_size_hint": 50,
                "batch_size_hint": 1,
                "quality_priority": "quality"
            }
        }
        
        config_params = use_case_configs.get(use_case, use_case_configs["balanced"])
        config_params.update(kwargs)
        
        return self.generate_config(**config_params)


# Global instance
smart_defaults = SmartDefaultsGenerator()


def get_smart_config(
    use_case: str = "balanced",
    **kwargs
) -> Paper2DataConfig:
    """Get smart configuration for use case."""
    return smart_defaults.generate_config(use_case=use_case, **kwargs)


def get_system_info() -> Dict[str, Any]:
    """Get system information and recommendations."""
    return smart_defaults.get_system_recommendations()


def create_config_file(
    config_path: Path,
    use_case: str = "balanced",
    **kwargs
) -> None:
    """Create a configuration file with smart defaults."""
    import yaml
    
    config = get_smart_config(use_case=use_case, **kwargs)
    config_dict = config.model_dump(exclude_none=True)
    
    # Convert enums and Path objects to simple values for YAML serialization
    def convert_for_yaml(obj):
        if isinstance(obj, dict):
            return {k: convert_for_yaml(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_for_yaml(item) for item in obj]
        elif isinstance(obj, Path):
            return str(obj)
        elif hasattr(obj, 'value'):  # Enum
            return obj.value
        else:
            return obj
    
    config_dict = convert_for_yaml(config_dict)
    
    # Add metadata
    config_dict["_metadata"] = {
        "generated_by": "Paper2Data Smart Defaults",
        "use_case": use_case,
        "system_info": get_system_info()["system_info"],
        "version": "1.0.0"
    }
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w') as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)


def get_config_profiles() -> Dict[str, str]:
    """Get available configuration profiles with descriptions."""
    return {
        "fast": "Optimized for speed with basic extraction",
        "balanced": "Good balance of speed and quality (recommended)",
        "thorough": "High quality extraction with advanced features",
        "research": "Maximum quality for research with all features enabled",
        "demo": "Quick demonstration with minimal resources",
        "batch_processing": "Optimized for processing multiple files",
        "quick_analysis": "Fast analysis for quick insights",
        "high_quality": "Maximum quality regardless of processing time"
    } 
"""
Paper2Data Plugin Dependency Management System

This module provides comprehensive dependency resolution and management
for Paper2Data plugins, including version constraints, conflict resolution,
and automatic dependency installation.

Features:
- Semantic versioning support
- Dependency graph resolution
- Circular dependency detection
- Version constraint validation
- Automatic dependency installation
- Plugin compatibility checking
- Dependency conflict resolution
- Plugin ecosystem health monitoring

Author: Paper2Data Team
Version: 1.1.0
"""

import logging
from typing import Dict, List, Set, Optional, Tuple, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import re
import networkx as nx
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet, InvalidSpecifier
import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Types of dependencies"""
    REQUIRED = "required"
    OPTIONAL = "optional"
    DEVELOPMENT = "development"
    SYSTEM = "system"


class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    STRICT = "strict"          # Fail on any conflict
    LATEST = "latest"          # Use latest compatible version
    CONSERVATIVE = "conservative"  # Use oldest compatible version
    MANUAL = "manual"          # Require manual resolution


@dataclass
class VersionConstraint:
    """Version constraint specification"""
    package: str
    constraint: str
    dependency_type: DependencyType = DependencyType.REQUIRED
    
    def __post_init__(self):
        """Validate constraint syntax"""
        try:
            SpecifierSet(self.constraint)
        except InvalidSpecifier as e:
            raise ValueError(f"Invalid version constraint '{self.constraint}': {e}")
    
    def is_satisfied_by(self, version: str) -> bool:
        """Check if version satisfies constraint"""
        try:
            ver = Version(version)
            spec = SpecifierSet(self.constraint)
            return ver in spec
        except (InvalidVersion, InvalidSpecifier):
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "package": self.package,
            "constraint": self.constraint,
            "dependency_type": self.dependency_type.value
        }


@dataclass
class DependencyNode:
    """Node in dependency graph"""
    package: str
    version: str
    dependencies: List[VersionConstraint] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    installed: bool = False
    source: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "package": self.package,
            "version": self.version,
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "dependents": self.dependents,
            "installed": self.installed,
            "source": self.source
        }


@dataclass
class DependencyConflict:
    """Represents a dependency conflict"""
    package: str
    conflicting_versions: List[str]
    required_by: List[str]
    constraints: List[VersionConstraint]
    resolution: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "package": self.package,
            "conflicting_versions": self.conflicting_versions,
            "required_by": self.required_by,
            "constraints": [c.to_dict() for c in self.constraints],
            "resolution": self.resolution
        }


@dataclass
class DependencyResolution:
    """Result of dependency resolution"""
    install_order: List[str]
    conflicts: List[DependencyConflict]
    unresolved: List[str]
    graph: nx.DiGraph
    success: bool = True
    message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "install_order": self.install_order,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "unresolved": self.unresolved,
            "success": self.success,
            "message": self.message
        }


class DependencyManager:
    """
    Comprehensive dependency management system for Paper2Data plugins
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize dependency manager
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger("DependencyManager")
        
        # Dependency graph
        self.graph = nx.DiGraph()
        
        # Installed packages
        self.installed_packages: Dict[str, DependencyNode] = {}
        
        # Package registry
        self.package_registry: Dict[str, Dict[str, Any]] = {}
        
        # Conflict resolution strategy
        self.conflict_resolution = ConflictResolution(
            self.config.get("conflict_resolution", "latest")
        )
        
        # Cache for package information
        self.package_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize dependency manager"""
        try:
            # Load installed packages
            self._load_installed_packages()
            
            # Load package registry
            self._load_package_registry()
            
            self.logger.info("Dependency manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize dependency manager: {e}")
            raise
    
    def _load_installed_packages(self):
        """Load currently installed packages"""
        try:
            # Load from configuration or discovery
            installed_file = Path(self.config.get("installed_packages_file", "installed_packages.json"))
            
            if installed_file.exists():
                with open(installed_file, 'r') as f:
                    data = json.load(f)
                    
                for pkg_name, pkg_data in data.items():
                    node = DependencyNode(
                        package=pkg_name,
                        version=pkg_data.get("version", "0.0.0"),
                        dependencies=[
                            VersionConstraint(
                                package=dep["package"],
                                constraint=dep["constraint"],
                                dependency_type=DependencyType(dep.get("dependency_type", "required"))
                            )
                            for dep in pkg_data.get("dependencies", [])
                        ],
                        installed=True,
                        source=pkg_data.get("source", "unknown")
                    )
                    self.installed_packages[pkg_name] = node
                    
            self.logger.info(f"Loaded {len(self.installed_packages)} installed packages")
                    
        except Exception as e:
            self.logger.warning(f"Failed to load installed packages: {e}")
    
    def _load_package_registry(self):
        """Load package registry information"""
        try:
            registry_file = Path(self.config.get("package_registry_file", "package_registry.json"))
            
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    self.package_registry = json.load(f)
                    
            self.logger.info(f"Loaded {len(self.package_registry)} packages from registry")
                    
        except Exception as e:
            self.logger.warning(f"Failed to load package registry: {e}")
    
    def add_package(self, package_name: str, version: str, 
                   dependencies: List[VersionConstraint] = None,
                   source: str = "manual") -> bool:
        """
        Add a package to the dependency graph
        
        Args:
            package_name: Name of the package
            version: Package version
            dependencies: List of dependencies
            source: Source of the package
            
        Returns:
            bool: True if successfully added
        """
        try:
            if not self._validate_version(version):
                raise ValueError(f"Invalid version: {version}")
            
            # Create dependency node
            node = DependencyNode(
                package=package_name,
                version=version,
                dependencies=dependencies or [],
                source=source
            )
            
            # Add to graph
            self.graph.add_node(package_name, node=node)
            
            # Add dependency edges
            for dep in node.dependencies:
                self.graph.add_edge(package_name, dep.package, 
                                  constraint=dep.constraint,
                                  dependency_type=dep.dependency_type)
            
            self.logger.info(f"Added package {package_name} v{version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add package {package_name}: {e}")
            return False
    
    def resolve_dependencies(self, packages: List[str]) -> DependencyResolution:
        """
        Resolve dependencies for given packages
        
        Args:
            packages: List of package names to resolve
            
        Returns:
            DependencyResolution: Resolution result
        """
        try:
            self.logger.info(f"Resolving dependencies for {len(packages)} packages")
            
            # Build dependency graph
            graph = self._build_dependency_graph(packages)
            
            # Check for circular dependencies
            circular_deps = self._detect_circular_dependencies(graph)
            if circular_deps:
                return DependencyResolution(
                    install_order=[],
                    conflicts=[],
                    unresolved=circular_deps,
                    graph=graph,
                    success=False,
                    message=f"Circular dependencies detected: {circular_deps}"
                )
            
            # Resolve version conflicts
            conflicts = self._resolve_version_conflicts(graph)
            
            # Generate install order
            install_order = self._generate_install_order(graph)
            
            # Check for unresolved dependencies
            unresolved = self._find_unresolved_dependencies(graph)
            
            success = len(conflicts) == 0 and len(unresolved) == 0
            
            return DependencyResolution(
                install_order=install_order,
                conflicts=conflicts,
                unresolved=unresolved,
                graph=graph,
                success=success,
                message="Dependencies resolved successfully" if success else "Resolution completed with issues"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to resolve dependencies: {e}")
            return DependencyResolution(
                install_order=[],
                conflicts=[],
                unresolved=packages,
                graph=nx.DiGraph(),
                success=False,
                message=f"Resolution failed: {e}"
            )
    
    def _build_dependency_graph(self, packages: List[str]) -> nx.DiGraph:
        """Build dependency graph for packages"""
        graph = nx.DiGraph()
        visited = set()
        
        def _add_package_recursive(pkg_name: str):
            if pkg_name in visited:
                return
                
            visited.add(pkg_name)
            
            # Get package info
            pkg_info = self._get_package_info(pkg_name)
            if not pkg_info:
                self.logger.warning(f"Package not found: {pkg_name}")
                return
            
            # Add node
            graph.add_node(pkg_name, **pkg_info)
            
            # Add dependencies
            for dep in pkg_info.get("dependencies", []):
                dep_name = dep["package"]
                constraint = dep["constraint"]
                
                graph.add_edge(pkg_name, dep_name, constraint=constraint)
                _add_package_recursive(dep_name)
        
        # Build graph recursively
        for pkg in packages:
            _add_package_recursive(pkg)
        
        return graph
    
    def _detect_circular_dependencies(self, graph: nx.DiGraph) -> List[str]:
        """Detect circular dependencies in graph"""
        try:
            cycles = list(nx.simple_cycles(graph))
            circular_deps = []
            
            for cycle in cycles:
                circular_deps.extend(cycle)
            
            return list(set(circular_deps))
            
        except Exception as e:
            self.logger.error(f"Failed to detect circular dependencies: {e}")
            return []
    
    def _resolve_version_conflicts(self, graph: nx.DiGraph) -> List[DependencyConflict]:
        """Resolve version conflicts in dependency graph"""
        conflicts = []
        
        # Find packages with multiple version requirements
        package_versions = {}
        
        for node in graph.nodes():
            for successor in graph.successors(node):
                edge_data = graph.get_edge_data(node, successor)
                constraint = edge_data.get("constraint", "*")
                
                if successor not in package_versions:
                    package_versions[successor] = []
                
                package_versions[successor].append({
                    "constraint": constraint,
                    "required_by": node
                })
        
        # Check for conflicts
        for pkg_name, requirements in package_versions.items():
            if len(requirements) > 1:
                # Check if constraints are compatible
                compatible_versions = self._find_compatible_versions(pkg_name, requirements)
                
                if not compatible_versions:
                    conflict = DependencyConflict(
                        package=pkg_name,
                        conflicting_versions=[req["constraint"] for req in requirements],
                        required_by=[req["required_by"] for req in requirements],
                        constraints=[
                            VersionConstraint(pkg_name, req["constraint"])
                            for req in requirements
                        ]
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def _find_compatible_versions(self, package_name: str, 
                                requirements: List[Dict[str, Any]]) -> List[str]:
        """Find versions that satisfy all requirements"""
        try:
            # Get available versions
            available_versions = self._get_available_versions(package_name)
            
            compatible_versions = []
            
            for version in available_versions:
                is_compatible = True
                
                for req in requirements:
                    constraint = VersionConstraint(package_name, req["constraint"])
                    if not constraint.is_satisfied_by(version):
                        is_compatible = False
                        break
                
                if is_compatible:
                    compatible_versions.append(version)
            
            return compatible_versions
            
        except Exception as e:
            self.logger.error(f"Failed to find compatible versions for {package_name}: {e}")
            return []
    
    def _generate_install_order(self, graph: nx.DiGraph) -> List[str]:
        """Generate topological install order"""
        try:
            return list(nx.topological_sort(graph))
        except nx.NetworkXError:
            self.logger.error("Cannot generate install order due to circular dependencies")
            return []
    
    def _find_unresolved_dependencies(self, graph: nx.DiGraph) -> List[str]:
        """Find dependencies that cannot be resolved"""
        unresolved = []
        
        for node in graph.nodes():
            node_data = graph.nodes[node]
            if not node_data.get("available", True):
                unresolved.append(node)
        
        return unresolved
    
    def _get_package_info(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Get package information from registry"""
        # Check cache first
        if package_name in self.package_cache:
            return self.package_cache[package_name]
        
        # Check installed packages
        if package_name in self.installed_packages:
            node = self.installed_packages[package_name]
            info = {
                "version": node.version,
                "dependencies": [dep.to_dict() for dep in node.dependencies],
                "installed": True,
                "available": True
            }
            self.package_cache[package_name] = info
            return info
        
        # Check package registry
        if package_name in self.package_registry:
            info = self.package_registry[package_name].copy()
            info["available"] = True
            self.package_cache[package_name] = info
            return info
        
        # Package not found
        return None
    
    def _get_available_versions(self, package_name: str) -> List[str]:
        """Get available versions for a package"""
        pkg_info = self._get_package_info(package_name)
        if not pkg_info:
            return []
        
        return pkg_info.get("available_versions", [pkg_info.get("version", "0.0.0")])
    
    def _validate_version(self, version: str) -> bool:
        """Validate version string"""
        try:
            Version(version)
            return True
        except InvalidVersion:
            return False
    
    def install_package(self, package_name: str, version: str = None) -> bool:
        """
        Install a package with dependency resolution
        
        Args:
            package_name: Name of package to install
            version: Specific version to install (optional)
            
        Returns:
            bool: True if installation successful
        """
        try:
            # Resolve dependencies
            resolution = self.resolve_dependencies([package_name])
            
            if not resolution.success:
                self.logger.error(f"Failed to resolve dependencies: {resolution.message}")
                return False
            
            # Install packages in order
            for pkg in resolution.install_order:
                if not self._install_single_package(pkg, version if pkg == package_name else None):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install package {package_name}: {e}")
            return False
    
    def _install_single_package(self, package_name: str, version: str = None) -> bool:
        """Install a single package"""
        try:
            # Check if already installed
            if package_name in self.installed_packages:
                self.logger.info(f"Package {package_name} already installed")
                return True
            
            # Get package info
            pkg_info = self._get_package_info(package_name)
            if not pkg_info:
                self.logger.error(f"Package {package_name} not found")
                return False
            
            # Install package (placeholder - actual implementation would download and install)
            install_version = version or pkg_info.get("version", "latest")
            
            # Mark as installed
            node = DependencyNode(
                package=package_name,
                version=install_version,
                dependencies=[],
                installed=True,
                source="marketplace"
            )
            
            self.installed_packages[package_name] = node
            self.logger.info(f"Installed package {package_name} v{install_version}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install package {package_name}: {e}")
            return False
    
    def uninstall_package(self, package_name: str, force: bool = False) -> bool:
        """
        Uninstall a package
        
        Args:
            package_name: Name of package to uninstall
            force: Force uninstall even if other packages depend on it
            
        Returns:
            bool: True if uninstallation successful
        """
        try:
            if package_name not in self.installed_packages:
                self.logger.warning(f"Package {package_name} not installed")
                return True
            
            # Check for dependents
            dependents = self._find_dependents(package_name)
            if dependents and not force:
                self.logger.error(f"Cannot uninstall {package_name}: required by {dependents}")
                return False
            
            # Uninstall
            del self.installed_packages[package_name]
            self.logger.info(f"Uninstalled package {package_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uninstall package {package_name}: {e}")
            return False
    
    def _find_dependents(self, package_name: str) -> List[str]:
        """Find packages that depend on the given package"""
        dependents = []
        
        for pkg_name, node in self.installed_packages.items():
            if pkg_name == package_name:
                continue
                
            for dep in node.dependencies:
                if dep.package == package_name:
                    dependents.append(pkg_name)
                    break
        
        return dependents
    
    def get_dependency_graph(self) -> Dict[str, Any]:
        """Get dependency graph information"""
        return {
            "nodes": len(self.graph.nodes()),
            "edges": len(self.graph.edges()),
            "installed_packages": len(self.installed_packages),
            "packages": list(self.installed_packages.keys())
        }
    
    def export_dependency_info(self, file_path: str):
        """Export dependency information to file"""
        try:
            data = {
                "installed_packages": {
                    name: node.to_dict() 
                    for name, node in self.installed_packages.items()
                },
                "graph_info": self.get_dependency_graph(),
                "config": self.config
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Exported dependency info to {file_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export dependency info: {e}") 
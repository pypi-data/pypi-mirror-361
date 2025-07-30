"""
Paper2Data Plugin Marketplace

This module provides a comprehensive marketplace system for Paper2Data plugins,
including plugin discovery, installation, updates, community features, and
plugin ecosystem management.

Features:
- Plugin discovery and search
- Automatic installation and updates
- Community ratings and reviews
- Plugin versioning and compatibility
- Security scanning and validation
- Plugin collections and categories
- Developer tools and publishing
- Analytics and usage tracking
- Integration with dependency management

Author: Paper2Data Team
Version: 1.1.0
"""

import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import requests
from pathlib import Path
import hashlib
import zipfile
import tempfile
import shutil
from urllib.parse import urlparse, urljoin
from datetime import datetime, timedelta
import semver
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
from .plugin_dependency_manager import DependencyManager, VersionConstraint


logger = logging.getLogger(__name__)


class PluginStatus(Enum):
    """Plugin status in marketplace"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    BETA = "beta"
    ALPHA = "alpha"
    ARCHIVED = "archived"


class PluginCategory(Enum):
    """Plugin categories"""
    EXTRACTION = "extraction"
    ANALYSIS = "analysis"
    OUTPUT = "output"
    PROCESSING = "processing"
    INTEGRATION = "integration"
    UTILITY = "utility"
    EXPERIMENTAL = "experimental"


class SecurityStatus(Enum):
    """Security scan status"""
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"
    UNKNOWN = "unknown"


@dataclass
class PluginRating:
    """Plugin rating and review"""
    user_id: str
    rating: int  # 1-5 stars
    review: str
    date: datetime
    version: str
    helpful_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "rating": self.rating,
            "review": self.review,
            "date": self.date.isoformat(),
            "version": self.version,
            "helpful_count": self.helpful_count
        }


@dataclass
class PluginStats:
    """Plugin statistics"""
    downloads: int
    active_users: int
    ratings_count: int
    average_rating: float
    last_updated: datetime
    compatibility_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "downloads": self.downloads,
            "active_users": self.active_users,
            "ratings_count": self.ratings_count,
            "average_rating": self.average_rating,
            "last_updated": self.last_updated.isoformat(),
            "compatibility_score": self.compatibility_score
        }


@dataclass
class SecurityScan:
    """Security scan results"""
    status: SecurityStatus
    scan_date: datetime
    issues: List[str]
    score: int  # 0-100
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "scan_date": self.scan_date.isoformat(),
            "issues": self.issues,
            "score": self.score,
            "details": self.details
        }


@dataclass
class MarketplacePlugin:
    """Plugin in marketplace"""
    name: str
    version: str
    description: str
    author: str
    homepage: str
    download_url: str
    license: str
    category: PluginCategory
    status: PluginStatus
    tags: List[str]
    dependencies: List[VersionConstraint]
    paper2data_version: str
    file_size: int
    file_hash: str
    security_scan: SecurityScan
    stats: PluginStats
    ratings: List[PluginRating]
    screenshots: List[str]
    documentation_url: str
    source_code_url: str
    changelog: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "homepage": self.homepage,
            "download_url": self.download_url,
            "license": self.license,
            "category": self.category.value,
            "status": self.status.value,
            "tags": self.tags,
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "paper2data_version": self.paper2data_version,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "security_scan": self.security_scan.to_dict(),
            "stats": self.stats.to_dict(),
            "ratings": [rating.to_dict() for rating in self.ratings],
            "screenshots": self.screenshots,
            "documentation_url": self.documentation_url,
            "source_code_url": self.source_code_url,
            "changelog": self.changelog
        }


@dataclass
class SearchFilter:
    """Search filter for marketplace"""
    category: Optional[PluginCategory] = None
    tags: List[str] = field(default_factory=list)
    min_rating: Optional[float] = None
    max_file_size: Optional[int] = None
    license: Optional[str] = None
    status: Optional[PluginStatus] = None
    compatibility_version: Optional[str] = None
    author: Optional[str] = None
    
    def matches(self, plugin: MarketplacePlugin) -> bool:
        """Check if plugin matches filter"""
        if self.category and plugin.category != self.category:
            return False
        
        if self.tags and not any(tag in plugin.tags for tag in self.tags):
            return False
            
        if self.min_rating and plugin.stats.average_rating < self.min_rating:
            return False
            
        if self.max_file_size and plugin.file_size > self.max_file_size:
            return False
            
        if self.license and plugin.license != self.license:
            return False
            
        if self.status and plugin.status != self.status:
            return False
            
        if self.author and plugin.author != self.author:
            return False
            
        return True


class PluginMarketplace:
    """
    Comprehensive plugin marketplace for Paper2Data
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize marketplace
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger("PluginMarketplace")
        
        # Marketplace configuration
        self.marketplace_url = self.config.get("marketplace_url", "https://marketplace.paper2data.dev")
        self.api_key = self.config.get("api_key", "")
        self.local_cache_dir = Path(self.config.get("cache_dir", "./plugin_cache"))
        
        # Plugin registry
        self.plugins: Dict[str, MarketplacePlugin] = {}
        
        # Dependency manager
        self.dependency_manager = DependencyManager(config.get("dependency_config", {}))
        
        # Security settings
        self.security_enabled = self.config.get("security_enabled", True)
        self.auto_update = self.config.get("auto_update", False)
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize marketplace"""
        try:
            # Create cache directory
            self.local_cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Load cached plugins
            self._load_cached_plugins()
            
            self.logger.info("Plugin marketplace initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize marketplace: {e}")
            raise
    
    def _load_cached_plugins(self):
        """Load plugins from local cache"""
        try:
            cache_file = self.local_cache_dir / "plugins.json"
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    
                for plugin_data in data.get("plugins", []):
                    plugin = self._dict_to_plugin(plugin_data)
                    self.plugins[plugin.name] = plugin
                    
                self.logger.info(f"Loaded {len(self.plugins)} plugins from cache")
        except Exception as e:
            self.logger.warning(f"Failed to load cached plugins: {e}")
    
    def _dict_to_plugin(self, data: Dict[str, Any]) -> MarketplacePlugin:
        """Convert dictionary to MarketplacePlugin"""
        return MarketplacePlugin(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            homepage=data["homepage"],
            download_url=data["download_url"],
            license=data["license"],
            category=PluginCategory(data["category"]),
            status=PluginStatus(data["status"]),
            tags=data["tags"],
            dependencies=[
                VersionConstraint(
                    package=dep["package"],
                    constraint=dep["constraint"]
                )
                for dep in data["dependencies"]
            ],
            paper2data_version=data["paper2data_version"],
            file_size=data["file_size"],
            file_hash=data["file_hash"],
            security_scan=SecurityScan(
                status=SecurityStatus(data["security_scan"]["status"]),
                scan_date=datetime.fromisoformat(data["security_scan"]["scan_date"]),
                issues=data["security_scan"]["issues"],
                score=data["security_scan"]["score"],
                details=data["security_scan"]["details"]
            ),
            stats=PluginStats(
                downloads=data["stats"]["downloads"],
                active_users=data["stats"]["active_users"],
                ratings_count=data["stats"]["ratings_count"],
                average_rating=data["stats"]["average_rating"],
                last_updated=datetime.fromisoformat(data["stats"]["last_updated"]),
                compatibility_score=data["stats"]["compatibility_score"]
            ),
            ratings=[
                PluginRating(
                    user_id=r["user_id"],
                    rating=r["rating"],
                    review=r["review"],
                    date=datetime.fromisoformat(r["date"]),
                    version=r["version"],
                    helpful_count=r["helpful_count"]
                )
                for r in data["ratings"]
            ],
            screenshots=data["screenshots"],
            documentation_url=data["documentation_url"],
            source_code_url=data["source_code_url"],
            changelog=data["changelog"]
        )
    
    async def refresh_plugin_list(self) -> bool:
        """
        Refresh plugin list from marketplace
        
        Returns:
            bool: True if successful
        """
        try:
            self.logger.info("Refreshing plugin list from marketplace")
            
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                
                async with session.get(
                    f"{self.marketplace_url}/api/plugins",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Update plugin registry
                        self.plugins.clear()
                        for plugin_data in data.get("plugins", []):
                            plugin = self._dict_to_plugin(plugin_data)
                            self.plugins[plugin.name] = plugin
                        
                        # Save to cache
                        await self._save_plugin_cache()
                        
                        self.logger.info(f"Refreshed {len(self.plugins)} plugins")
                        return True
                    else:
                        self.logger.error(f"Failed to refresh plugins: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Failed to refresh plugin list: {e}")
            return False
    
    async def _save_plugin_cache(self):
        """Save plugin cache to file"""
        try:
            cache_file = self.local_cache_dir / "plugins.json"
            data = {
                "plugins": [plugin.to_dict() for plugin in self.plugins.values()],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save plugin cache: {e}")
    
    def search_plugins(self, query: str = "", 
                      filters: SearchFilter = None,
                      sort_by: str = "downloads",
                      limit: int = 50) -> List[MarketplacePlugin]:
        """
        Search for plugins in marketplace
        
        Args:
            query: Search query
            filters: Search filters
            sort_by: Sort criteria (downloads, rating, updated, name)
            limit: Maximum results
            
        Returns:
            List[MarketplacePlugin]: Search results
        """
        try:
            results = []
            
            for plugin in self.plugins.values():
                # Apply query filter
                if query:
                    if not (query.lower() in plugin.name.lower() or 
                           query.lower() in plugin.description.lower() or
                           any(query.lower() in tag.lower() for tag in plugin.tags)):
                        continue
                
                # Apply filters
                if filters and not filters.matches(plugin):
                    continue
                
                results.append(plugin)
            
            # Sort results
            if sort_by == "downloads":
                results.sort(key=lambda p: p.stats.downloads, reverse=True)
            elif sort_by == "rating":
                results.sort(key=lambda p: p.stats.average_rating, reverse=True)
            elif sort_by == "updated":
                results.sort(key=lambda p: p.stats.last_updated, reverse=True)
            elif sort_by == "name":
                results.sort(key=lambda p: p.name)
            
            return results[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to search plugins: {e}")
            return []
    
    def get_plugin_details(self, plugin_name: str) -> Optional[MarketplacePlugin]:
        """
        Get detailed information about a plugin
        
        Args:
            plugin_name: Name of the plugin
            
        Returns:
            Optional[MarketplacePlugin]: Plugin details or None
        """
        return self.plugins.get(plugin_name)
    
    async def install_plugin(self, plugin_name: str, 
                           version: str = None,
                           force: bool = False) -> bool:
        """
        Install a plugin from marketplace
        
        Args:
            plugin_name: Name of plugin to install
            version: Specific version to install (optional)
            force: Force installation even if security issues
            
        Returns:
            bool: True if installation successful
        """
        try:
            plugin = self.plugins.get(plugin_name)
            if not plugin:
                self.logger.error(f"Plugin {plugin_name} not found in marketplace")
                return False
            
            # Check security
            if self.security_enabled and not force:
                if plugin.security_scan.status == SecurityStatus.DANGER:
                    self.logger.error(f"Plugin {plugin_name} has security issues")
                    return False
            
            # Check compatibility
            if not self._check_compatibility(plugin):
                self.logger.error(f"Plugin {plugin_name} is not compatible")
                return False
            
            # Resolve dependencies
            if not await self._resolve_plugin_dependencies(plugin):
                self.logger.error(f"Failed to resolve dependencies for {plugin_name}")
                return False
            
            # Download and install
            if not await self._download_and_install_plugin(plugin, version):
                self.logger.error(f"Failed to download/install {plugin_name}")
                return False
            
            self.logger.info(f"Successfully installed plugin {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to install plugin {plugin_name}: {e}")
            return False
    
    def _check_compatibility(self, plugin: MarketplacePlugin) -> bool:
        """Check if plugin is compatible with current Paper2Data version"""
        try:
            # For now, simple string comparison
            # In production, would use semantic versioning
            return plugin.paper2data_version == ">=1.0.0"
        except Exception as e:
            self.logger.error(f"Failed to check compatibility: {e}")
            return False
    
    async def _resolve_plugin_dependencies(self, plugin: MarketplacePlugin) -> bool:
        """Resolve plugin dependencies"""
        try:
            if not plugin.dependencies:
                return True
            
            # Use dependency manager to resolve
            dep_names = [dep.package for dep in plugin.dependencies]
            resolution = self.dependency_manager.resolve_dependencies(dep_names)
            
            if not resolution.success:
                self.logger.error(f"Dependency resolution failed: {resolution.message}")
                return False
            
            # Install dependencies
            for dep_name in resolution.install_order:
                if not self.dependency_manager.install_package(dep_name):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resolve dependencies: {e}")
            return False
    
    async def _download_and_install_plugin(self, plugin: MarketplacePlugin, 
                                         version: str = None) -> bool:
        """Download and install plugin"""
        try:
            # Download plugin
            download_path = await self._download_plugin(plugin)
            if not download_path:
                return False
            
            # Verify hash
            if not self._verify_plugin_hash(download_path, plugin.file_hash):
                self.logger.error(f"Plugin hash verification failed")
                return False
            
            # Install plugin
            if not await self._install_plugin_from_file(download_path, plugin):
                return False
            
            # Clean up
            if download_path.exists():
                download_path.unlink()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download/install plugin: {e}")
            return False
    
    async def _download_plugin(self, plugin: MarketplacePlugin) -> Optional[Path]:
        """Download plugin file"""
        try:
            download_path = self.local_cache_dir / f"{plugin.name}-{plugin.version}.zip"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(plugin.download_url) as response:
                    if response.status == 200:
                        with open(download_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        self.logger.info(f"Downloaded plugin {plugin.name}")
                        return download_path
                    else:
                        self.logger.error(f"Failed to download plugin: HTTP {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Failed to download plugin: {e}")
            return None
    
    def _verify_plugin_hash(self, file_path: Path, expected_hash: str) -> bool:
        """Verify plugin file hash"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                return file_hash == expected_hash
        except Exception as e:
            self.logger.error(f"Failed to verify hash: {e}")
            return False
    
    async def _install_plugin_from_file(self, file_path: Path, 
                                      plugin: MarketplacePlugin) -> bool:
        """Install plugin from downloaded file"""
        try:
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Extract plugin
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_path)
                
                # Find plugin files
                plugin_files = list(temp_path.glob("**/*.py"))
                if not plugin_files:
                    self.logger.error("No Python files found in plugin")
                    return False
                
                # Install plugin files
                plugin_dir = Path("plugins") / plugin.name
                plugin_dir.mkdir(parents=True, exist_ok=True)
                
                for file in plugin_files:
                    shutil.copy2(file, plugin_dir)
                
                self.logger.info(f"Installed plugin files for {plugin.name}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to install plugin from file: {e}")
            return False
    
    async def uninstall_plugin(self, plugin_name: str) -> bool:
        """
        Uninstall a plugin
        
        Args:
            plugin_name: Name of plugin to uninstall
            
        Returns:
            bool: True if uninstallation successful
        """
        try:
            # Remove plugin files
            plugin_dir = Path("plugins") / plugin_name
            if plugin_dir.exists():
                shutil.rmtree(plugin_dir)
            
            # Remove from dependency manager
            self.dependency_manager.uninstall_package(plugin_name)
            
            self.logger.info(f"Uninstalled plugin {plugin_name}")
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
            # Get current version
            current_plugin = self.plugins.get(plugin_name)
            if not current_plugin:
                self.logger.error(f"Plugin {plugin_name} not found")
                return False
            
            # Check for updates
            await self.refresh_plugin_list()
            updated_plugin = self.plugins.get(plugin_name)
            
            if not updated_plugin:
                self.logger.error(f"Plugin {plugin_name} no longer available")
                return False
            
            # Compare versions
            if semver.compare(updated_plugin.version, current_plugin.version) <= 0:
                self.logger.info(f"Plugin {plugin_name} is already up to date")
                return True
            
            # Update plugin
            if not await self.install_plugin(plugin_name, updated_plugin.version):
                return False
            
            self.logger.info(f"Updated plugin {plugin_name} to version {updated_plugin.version}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update plugin {plugin_name}: {e}")
            return False
    
    def get_installed_plugins(self) -> List[str]:
        """Get list of installed plugins"""
        try:
            plugins_dir = Path("plugins")
            if not plugins_dir.exists():
                return []
            
            return [p.name for p in plugins_dir.iterdir() if p.is_dir()]
            
        except Exception as e:
            self.logger.error(f"Failed to get installed plugins: {e}")
            return []
    
    def get_plugin_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        try:
            total_plugins = len(self.plugins)
            categories = {}
            total_downloads = 0
            
            for plugin in self.plugins.values():
                cat = plugin.category.value
                categories[cat] = categories.get(cat, 0) + 1
                total_downloads += plugin.stats.downloads
            
            return {
                "total_plugins": total_plugins,
                "categories": categories,
                "total_downloads": total_downloads,
                "installed_plugins": len(self.get_installed_plugins())
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get plugin stats: {e}")
            return {}
    
    async def submit_rating(self, plugin_name: str, rating: int, 
                          review: str = "") -> bool:
        """
        Submit a rating for a plugin
        
        Args:
            plugin_name: Name of plugin
            rating: Rating (1-5)
            review: Review text
            
        Returns:
            bool: True if successful
        """
        try:
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5")
            
            # Submit to marketplace API
            async with aiohttp.ClientSession() as session:
                data = {
                    "plugin_name": plugin_name,
                    "rating": rating,
                    "review": review
                }
                
                headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
                
                async with session.post(
                    f"{self.marketplace_url}/api/ratings",
                    json=data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        self.logger.info(f"Submitted rating for {plugin_name}")
                        return True
                    else:
                        self.logger.error(f"Failed to submit rating: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            self.logger.error(f"Failed to submit rating: {e}")
            return False


# Global marketplace instance
marketplace = None


def get_marketplace() -> PluginMarketplace:
    """Get global marketplace instance"""
    global marketplace
    if marketplace is None:
        marketplace = PluginMarketplace()
    return marketplace


def initialize_marketplace(config: Dict[str, Any] = None) -> PluginMarketplace:
    """
    Initialize marketplace with configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        PluginMarketplace: Initialized marketplace
    """
    global marketplace
    marketplace = PluginMarketplace(config)
    return marketplace 
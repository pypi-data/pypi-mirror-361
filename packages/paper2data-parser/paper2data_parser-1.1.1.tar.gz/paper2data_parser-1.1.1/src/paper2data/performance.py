"""
Performance optimization module for Paper2Data.

Implements Stage 4 requirements:
- Multiprocessing for large batch operations
- Memory optimization for large PDF files
- Streaming processing for continuous data flows
- Result caching to avoid reprocessing
- Progress persistence for resumable operations
- Resource usage monitoring and reporting
- Automatic scaling based on system resources
"""

import os
import gc
import sys
import time
import json
import pickle
import hashlib
import tempfile
import threading
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import Manager, Queue, Value, Lock
from typing import Dict, List, Any, Optional, Callable, Union, Iterator
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps
import logging

import psutil
from cachetools import TTLCache
from .utils import get_logger, ProcessingError, progress_callback

logger = get_logger(__name__)

# Global constants
DEFAULT_CACHE_SIZE = 1000
DEFAULT_CACHE_TTL = 3600  # 1 hour
DEFAULT_WORKER_COUNT = None  # Auto-detect
DEFAULT_MEMORY_THRESHOLD = 0.8  # 80% memory usage trigger
DEFAULT_CHECKPOINT_INTERVAL = 10  # Save progress every 10 operations

@dataclass
class ResourceMetrics:
    """System resource usage metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available: int
    memory_used: int
    disk_usage: float
    active_processes: int
    extraction_rate: float = 0.0  # Operations per second
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class ProcessingCheckpoint:
    """Checkpoint for resumable operations."""
    operation_id: str
    total_items: int
    completed_items: int
    failed_items: List[str]
    start_time: datetime
    last_update: datetime
    results: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['last_update'] = self.last_update.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessingCheckpoint':
        """Create from dictionary."""
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['last_update'] = datetime.fromisoformat(data['last_update'])
        return cls(**data)

class ResourceMonitor:
    """Monitor system resource usage and provide optimization recommendations."""
    
    def __init__(self, monitoring_interval: float = 1.0):
        self.monitoring_interval = monitoring_interval
        self.metrics_history: List[ResourceMetrics] = []
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
    def start_monitoring(self):
        """Start resource monitoring in background thread."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Resource monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                with self.lock:
                    self.metrics_history.append(metrics)
                    # Keep only last 1000 metrics to prevent memory bloat
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]
                
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_metrics(self) -> ResourceMetrics:
        """Collect current system metrics."""
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return ResourceMetrics(
            timestamp=datetime.now(),
            cpu_percent=psutil.cpu_percent(interval=None),
            memory_percent=memory.percent,
            memory_available=memory.available,
            memory_used=memory.used,
            disk_usage=disk.percent,
            active_processes=len(psutil.pids())
        )
    
    def get_current_metrics(self) -> ResourceMetrics:
        """Get current system metrics."""
        return self._collect_metrics()
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Get optimization recommendations based on current metrics."""
        metrics = self.get_current_metrics()
        recommendations = {
            "optimal_worker_count": self._calculate_optimal_workers(metrics),
            "memory_optimization_needed": metrics.memory_percent > DEFAULT_MEMORY_THRESHOLD,
            "batch_size_recommendation": self._calculate_optimal_batch_size(metrics),
            "resource_warnings": []
        }
        
        # Add warnings for resource constraints
        if metrics.memory_percent > 90:
            recommendations["resource_warnings"].append("High memory usage detected - consider processing smaller batches")
        if metrics.cpu_percent > 90:
            recommendations["resource_warnings"].append("High CPU usage detected - consider reducing worker count")
        if metrics.disk_usage > 90:
            recommendations["resource_warnings"].append("Low disk space - consider cleaning up temporary files")
        
        return recommendations
    
    def _calculate_optimal_workers(self, metrics: ResourceMetrics) -> int:
        """Calculate optimal number of workers based on system resources."""
        cpu_count = psutil.cpu_count()
        
        # Base worker count on CPU cores
        base_workers = cpu_count
        
        # Adjust based on memory availability
        if metrics.memory_percent > 70:
            base_workers = max(1, base_workers // 2)
        elif metrics.memory_percent > 80:
            base_workers = max(1, base_workers // 3)
        elif metrics.memory_percent > 90:
            base_workers = 1
        
        # Adjust based on CPU usage
        if metrics.cpu_percent > 80:
            base_workers = max(1, base_workers // 2)
        
        return min(base_workers, cpu_count)
    
    def _calculate_optimal_batch_size(self, metrics: ResourceMetrics) -> int:
        """Calculate optimal batch size based on available memory."""
        # Estimate batch size based on available memory
        # Assume ~100MB per document on average
        available_gb = metrics.memory_available / (1024 ** 3)
        estimated_batch_size = max(1, int(available_gb * 10))  # 10 docs per GB
        
        return min(estimated_batch_size, 50)  # Cap at 50 docs per batch

class PerformanceCache:
    """High-performance caching system for extraction results."""
    
    def __init__(self, max_size: int = DEFAULT_CACHE_SIZE, ttl: int = DEFAULT_CACHE_TTL):
        self.memory_cache = TTLCache(maxsize=max_size, ttl=ttl)
        self.disk_cache_dir = Path(tempfile.gettempdir()) / "paper2data_cache"
        self.disk_cache_dir.mkdir(exist_ok=True)
        self.cache_lock = threading.Lock()
        
    def _generate_cache_key(self, content: bytes, extraction_type: str = "all") -> str:
        """Generate cache key from content hash and extraction type."""
        content_hash = hashlib.md5(content).hexdigest()
        return f"{extraction_type}_{content_hash}"
    
    def get(self, content: bytes, extraction_type: str = "all") -> Optional[Dict[str, Any]]:
        """Get cached extraction results."""
        cache_key = self._generate_cache_key(content, extraction_type)
        
        with self.cache_lock:
            # Try memory cache first
            if cache_key in self.memory_cache:
                logger.debug(f"Cache hit (memory): {cache_key}")
                return self.memory_cache[cache_key]
            
            # Try disk cache
            disk_path = self.disk_cache_dir / f"{cache_key}.pkl"
            if disk_path.exists():
                try:
                    with open(disk_path, 'rb') as f:
                        result = pickle.load(f)
                    # Load back to memory cache
                    self.memory_cache[cache_key] = result
                    logger.debug(f"Cache hit (disk): {cache_key}")
                    return result
                except Exception as e:
                    logger.warning(f"Failed to load disk cache {cache_key}: {e}")
                    disk_path.unlink(missing_ok=True)
        
        return None
    
    def set(self, content: bytes, result: Dict[str, Any], extraction_type: str = "all"):
        """Store extraction results in cache."""
        cache_key = self._generate_cache_key(content, extraction_type)
        
        with self.cache_lock:
            # Store in memory cache
            self.memory_cache[cache_key] = result
            
            # Store in disk cache for persistence
            disk_path = self.disk_cache_dir / f"{cache_key}.pkl"
            try:
                with open(disk_path, 'wb') as f:
                    pickle.dump(result, f)
                logger.debug(f"Cache stored: {cache_key}")
            except Exception as e:
                logger.warning(f"Failed to store disk cache {cache_key}: {e}")
    
    def clear(self):
        """Clear all cached data."""
        with self.cache_lock:
            self.memory_cache.clear()
            # Clear disk cache
            for cache_file in self.disk_cache_dir.glob("*.pkl"):
                try:
                    cache_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to delete cache file {cache_file}: {e}")
        logger.info("Cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.cache_lock:
            disk_files = list(self.disk_cache_dir.glob("*.pkl"))
            disk_size = sum(f.stat().st_size for f in disk_files)
            
            return {
                "memory_cache_size": len(self.memory_cache),
                "memory_cache_max": self.memory_cache.maxsize,
                "disk_cache_files": len(disk_files),
                "disk_cache_size_mb": disk_size / (1024 * 1024),
                "hit_ratio": getattr(self.memory_cache, 'hit_ratio', 0.0)
            }

class ProgressPersistence:
    """Handle progress persistence for resumable operations."""
    
    def __init__(self, checkpoint_dir: Optional[Path] = None):
        self.checkpoint_dir = checkpoint_dir or Path(tempfile.gettempdir()) / "paper2data_checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.active_checkpoints: Dict[str, ProcessingCheckpoint] = {}
        self.lock = threading.Lock()
    
    def create_checkpoint(self, operation_id: str, total_items: int) -> ProcessingCheckpoint:
        """Create a new processing checkpoint."""
        checkpoint = ProcessingCheckpoint(
            operation_id=operation_id,
            total_items=total_items,
            completed_items=0,
            failed_items=[],
            start_time=datetime.now(),
            last_update=datetime.now(),
            results={}
        )
        
        with self.lock:
            self.active_checkpoints[operation_id] = checkpoint
        
        self._save_checkpoint(checkpoint)
        return checkpoint
    
    def update_checkpoint(self, operation_id: str, completed_items: int, 
                         failed_items: List[str] = None, results: Dict[str, Any] = None):
        """Update checkpoint progress."""
        with self.lock:
            if operation_id not in self.active_checkpoints:
                return
            
            checkpoint = self.active_checkpoints[operation_id]
            checkpoint.completed_items = completed_items
            checkpoint.last_update = datetime.now()
            
            if failed_items:
                checkpoint.failed_items.extend(failed_items)
            
            if results:
                checkpoint.results.update(results)
        
        self._save_checkpoint(checkpoint)
    
    def load_checkpoint(self, operation_id: str) -> Optional[ProcessingCheckpoint]:
        """Load checkpoint from disk."""
        checkpoint_path = self.checkpoint_dir / f"{operation_id}.json"
        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, 'r') as f:
                    data = json.load(f)
                checkpoint = ProcessingCheckpoint.from_dict(data)
                
                with self.lock:
                    self.active_checkpoints[operation_id] = checkpoint
                
                return checkpoint
            except Exception as e:
                logger.error(f"Failed to load checkpoint {operation_id}: {e}")
        
        return None
    
    def _save_checkpoint(self, checkpoint: ProcessingCheckpoint):
        """Save checkpoint to disk."""
        checkpoint_path = self.checkpoint_dir / f"{checkpoint.operation_id}.json"
        try:
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save checkpoint {checkpoint.operation_id}: {e}")
    
    def complete_checkpoint(self, operation_id: str):
        """Mark checkpoint as completed and clean up."""
        with self.lock:
            if operation_id in self.active_checkpoints:
                del self.active_checkpoints[operation_id]
        
        checkpoint_path = self.checkpoint_dir / f"{operation_id}.json"
        checkpoint_path.unlink(missing_ok=True)
        logger.info(f"Checkpoint {operation_id} completed and cleaned up")

class StreamingProcessor:
    """Process large datasets with streaming and memory optimization."""
    
    def __init__(self, chunk_size: int = 10, memory_threshold: float = DEFAULT_MEMORY_THRESHOLD):
        self.chunk_size = chunk_size
        self.memory_threshold = memory_threshold
        self.resource_monitor = ResourceMonitor()
    
    def process_stream(self, data_stream: Iterator[Any], 
                      processor_func: Callable[[Any], Any]) -> Iterator[Any]:
        """Process data stream with memory optimization."""
        self.resource_monitor.start_monitoring()
        
        try:
            chunk = []
            for item in data_stream:
                chunk.append(item)
                
                # Process chunk when full or memory threshold reached
                if len(chunk) >= self.chunk_size or self._should_process_chunk():
                    yield from self._process_chunk(chunk, processor_func)
                    chunk = []
                    self._optimize_memory()
            
            # Process remaining items
            if chunk:
                yield from self._process_chunk(chunk, processor_func)
        
        finally:
            self.resource_monitor.stop_monitoring()
    
    def _should_process_chunk(self) -> bool:
        """Check if chunk should be processed based on memory usage."""
        metrics = self.resource_monitor.get_current_metrics()
        return metrics.memory_percent > self.memory_threshold * 100
    
    def _process_chunk(self, chunk: List[Any], processor_func: Callable[[Any], Any]) -> Iterator[Any]:
        """Process a chunk of data."""
        for item in chunk:
            try:
                result = processor_func(item)
                yield result
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                yield None
    
    def _optimize_memory(self):
        """Optimize memory usage by forcing garbage collection."""
        gc.collect()
        # Additional memory optimization could be added here

class ParallelExtractor:
    """High-performance parallel extraction system."""
    
    def __init__(self, max_workers: Optional[int] = None, 
                 enable_caching: bool = True,
                 enable_monitoring: bool = True):
        self.max_workers = max_workers or psutil.cpu_count()
        self.cache = PerformanceCache() if enable_caching else None
        self.monitor = ResourceMonitor() if enable_monitoring else None
        self.progress_persistence = ProgressPersistence()
        
        # Dynamic worker adjustment
        self.current_workers = self.max_workers
        self.adjustment_lock = threading.Lock()
    
    def extract_parallel(self, pdf_content: bytes, extraction_types: List[str] = None, 
                         output_format: str = None, output_path: str = None) -> Dict[str, Any]:
        """Extract content using parallel processing with optional output formatting."""
        if extraction_types is None:
            extraction_types = ["content", "sections", "figures", "tables", "citations", "equations", "advanced_figures", "metadata", "citation_networks"]
        
        # Check cache first
        if self.cache:
            cached_result = self.cache.get(pdf_content, "_".join(extraction_types))
            if cached_result:
                logger.info("Using cached extraction results")
                return cached_result
        
        # Start monitoring
        if self.monitor:
            self.monitor.start_monitoring()
        
        try:
            # Parallel extraction
            results = self._extract_parallel_internal(pdf_content, extraction_types)
            
            # Cache results
            if self.cache:
                self.cache.set(pdf_content, results, "_".join(extraction_types))
            
            # Apply output formatting if requested
            if output_format and output_path:
                self._apply_output_formatting(results, output_format, output_path)
            
            return results
        
        finally:
            if self.monitor:
                self.monitor.stop_monitoring()
    
    def _extract_parallel_internal(self, pdf_content: bytes, 
                                  extraction_types: List[str]) -> Dict[str, Any]:
        """Internal parallel extraction implementation."""
        from datetime import datetime
        from .extractor import (ContentExtractor, SectionExtractor, 
                              FigureExtractor, TableExtractor, CitationExtractor)
        
        # Map extraction types to extractor classes
        extractor_map = {
            "content": ContentExtractor,
            "sections": SectionExtractor,
            "figures": FigureExtractor,
            "tables": TableExtractor,
            "citations": CitationExtractor
        }
        
        results = {
            "extraction_timestamp": datetime.now().isoformat(),
            "summary": {}
        }
        
        # Adjust worker count based on system resources
        if self.monitor:
            recommendations = self.monitor.get_recommendations()
            with self.adjustment_lock:
                self.current_workers = min(
                    recommendations["optimal_worker_count"],
                    len(extraction_types)
                )
        
        # Execute extractions in parallel
        with ThreadPoolExecutor(max_workers=self.current_workers) as executor:
            # Submit all extraction tasks
            future_to_type = {}
            for extraction_type in extraction_types:
                if extraction_type in extractor_map:
                    extractor_class = extractor_map[extraction_type]
                    future = executor.submit(self._run_extractor, extractor_class, pdf_content)
                    future_to_type[future] = extraction_type
                elif extraction_type == "equations":
                    # Handle equation processing separately
                    future = executor.submit(self._run_equation_processor, pdf_content)
                    future_to_type[future] = extraction_type
                elif extraction_type == "advanced_figures":
                    # Handle advanced figure processing separately
                    future = executor.submit(self._run_advanced_figure_processor, pdf_content)
                    future_to_type[future] = extraction_type
                elif extraction_type == "metadata":
                    # Handle metadata extraction separately
                    future = executor.submit(self._run_metadata_extractor, pdf_content)
                    future_to_type[future] = extraction_type
                elif extraction_type == "citation_networks":
                    # Handle citation network analysis separately
                    future = executor.submit(self._run_citation_network_analyzer, pdf_content)
                    future_to_type[future] = extraction_type
            
            # Collect results as they complete
            for future in as_completed(future_to_type):
                extraction_type = future_to_type[future]
                try:
                    result = future.result()
                    results[extraction_type] = result
                    logger.info(f"Completed {extraction_type} extraction")
                except Exception as e:
                    logger.error(f"Failed {extraction_type} extraction: {e}")
                    results[extraction_type] = {}
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def _run_extractor(self, extractor_class, pdf_content: bytes) -> Dict[str, Any]:
        """Run a single extractor with error handling."""
        try:
            extractor = extractor_class(pdf_content)
            return extractor.extract()
        except Exception as e:
            logger.error(f"Extractor {extractor_class.__name__} failed: {e}")
            return {}
    
    def _run_equation_processor(self, pdf_content: bytes) -> Dict[str, Any]:
        """Run equation processor with error handling."""
        try:
            from .equation_processor import process_equations_from_pdf
            return process_equations_from_pdf(pdf_content)
        except ImportError:
            logger.warning("Equation processor not available")
            return {"total_equations": 0, "equations": [], "processing_status": "not_available"}
        except Exception as e:
            logger.error(f"Equation processor failed: {e}")
            return {"total_equations": 0, "equations": [], "processing_status": "failed", "error": str(e)}
    
    def _run_advanced_figure_processor(self, pdf_content: bytes) -> Dict[str, Any]:
        """Run advanced figure processor with error handling."""
        try:
            from .advanced_figure_processor import process_advanced_figures
            return process_advanced_figures(pdf_content)
        except ImportError:
            logger.warning("Advanced figure processor not available")
            return {"total_figures": 0, "figures": [], "total_captions": 0, "captions": [], "processing_status": "not_available"}
        except Exception as e:
            logger.error(f"Advanced figure processor failed: {e}")
            return {"total_figures": 0, "figures": [], "total_captions": 0, "captions": [], "processing_status": "failed", "error": str(e)}
    
    def _run_metadata_extractor(self, pdf_content: bytes) -> Dict[str, Any]:
        """Run metadata extractor with error handling."""
        try:
            from .metadata_extractor import extract_metadata
            import tempfile
            import os
            
            # Create temporary file for metadata extraction
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_content)
                tmp_file_path = tmp_file.name
            
            try:
                metadata = extract_metadata(tmp_file_path)
                return metadata.to_dict()
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
        except ImportError:
            logger.warning("Metadata extractor not available")
            return {"processing_status": "not_available"}
        except Exception as e:
            logger.error(f"Metadata extractor failed: {e}")
            return {"processing_status": "failed", "error": str(e)}
    
    def _run_citation_network_analyzer(self, pdf_content: bytes) -> Dict[str, Any]:
        """Run citation network analyzer with error handling."""
        try:
            from .citation_network_analyzer import analyze_citation_networks
            from .metadata_extractor import extract_metadata
            import tempfile
            import os
            
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Extract metadata first (required for network analysis)
                metadata = extract_metadata(tmp_file_path)
                papers_metadata = [metadata.to_dict()]
                
                # Analyze citation networks
                network_results = analyze_citation_networks(papers_metadata)
                return network_results
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
        except ImportError:
            logger.warning("Citation network analyzer not available")
            return {"processing_status": "not_available"}
        except Exception as e:
            logger.error(f"Citation network analyzer failed: {e}")
            return {"processing_status": "failed", "error": str(e)}
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics from extraction results."""
        summary = {}
        
        # Content statistics
        if "content" in results:
            content_stats = results["content"].get("statistics", {})
            summary.update({
                "total_pages": content_stats.get("page_count", 0),
                "total_words": content_stats.get("word_count", 0)
            })
        
        # Section statistics
        if "sections" in results:
            summary["sections_found"] = results["sections"].get("section_count", 0)
        
        # Figure statistics
        if "figures" in results:
            summary["figures_found"] = results["figures"].get("figure_count", 0)
        
        # Table statistics
        if "tables" in results:
            summary["tables_found"] = results["tables"].get("total_tables", 0)
        
        # Citation statistics
        if "citations" in results:
            summary["references_found"] = results["citations"].get("reference_count", 0)
        
        # Equation statistics
        if "equations" in results:
            summary["equations_found"] = results["equations"].get("total_equations", 0)
        
        # Advanced figure statistics
        if "advanced_figures" in results:
            summary["advanced_figures_found"] = results["advanced_figures"].get("total_figures", 0)
            summary["captions_found"] = results["advanced_figures"].get("total_captions", 0)
        
        # Metadata statistics
        if "metadata" in results:
            metadata = results["metadata"]
            summary["metadata_extracted"] = metadata.get("processing_status", "unknown") not in ["not_available", "failed"]
            summary["authors_found"] = len(metadata.get("authors", []))
            summary["keywords_found"] = len(metadata.get("keywords", []))
            summary["citations_in_metadata"] = len(metadata.get("citations", []))
            summary["doi_found"] = bool(metadata.get("doi"))
            summary["title_confidence"] = metadata.get("title_confidence", 0.0)
            summary["abstract_confidence"] = metadata.get("abstract_confidence", 0.0)
            summary["author_confidence"] = metadata.get("author_confidence", 0.0)
        
        # Citation network statistics
        if "citation_networks" in results:
            networks = results["citation_networks"]
            summary["citation_networks_analyzed"] = networks.get("processing_status", "unknown") not in ["not_available", "failed"]
            summary["total_papers_in_network"] = networks.get("total_papers_analyzed", 0)
            summary["network_types_built"] = len(networks.get("networks", {}))
            
            # Add specific network metrics if available
            if "networks" in networks:
                for network_name, network_data in networks["networks"].items():
                    if "basic_metrics" in network_data:
                        metrics = network_data["basic_metrics"]
                        summary[f"{network_name}_nodes"] = metrics.get("num_nodes", 0)
                        summary[f"{network_name}_edges"] = metrics.get("num_edges", 0)
                        summary[f"{network_name}_density"] = metrics.get("density", 0.0)
        
        return summary

    def _apply_output_formatting(self, results: Dict[str, Any], output_format: str, output_path: str):
        """Apply output formatting to extraction results"""
        try:
            from .output_formatters import format_output
            success = format_output(results, output_path, output_format)
            if success:
                logger.info(f"Results formatted and saved to {output_path} in {output_format} format")
                results["output_formatted"] = {"format": output_format, "path": output_path, "success": True}
            else:
                logger.warning(f"Failed to format results in {output_format} format")
                results["output_formatted"] = {"format": output_format, "path": output_path, "success": False}
        except ImportError:
            logger.warning("Output formatting not available")
            results["output_formatted"] = {"error": "Output formatting not available"}
        except Exception as e:
            logger.error(f"Output formatting failed: {str(e)}")
            results["output_formatted"] = {"error": str(e)}

class BatchProcessor:
    """Process large batches of documents with full Stage 4 optimizations."""
    
    def __init__(self, max_workers: Optional[int] = None,
                 enable_caching: bool = True,
                 enable_monitoring: bool = True,
                 checkpoint_interval: int = DEFAULT_CHECKPOINT_INTERVAL):
        self.parallel_extractor = ParallelExtractor(max_workers, enable_caching, enable_monitoring)
        self.streaming_processor = StreamingProcessor()
        self.checkpoint_interval = checkpoint_interval
        self.progress_persistence = ProgressPersistence()
    
    def process_batch(self, documents: List[Union[str, bytes]], 
                     operation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a batch of documents with full optimization."""
        operation_id = operation_id or f"batch_{int(time.time())}"
        
        # Create checkpoint
        checkpoint = self.progress_persistence.create_checkpoint(operation_id, len(documents))
        
        try:
            results = []
            failed_items = []
            
            # Process documents in streaming fashion
            for i, doc in enumerate(documents):
                try:
                    if isinstance(doc, str):
                        # Handle file path or URL
                        doc_content = self._load_document(doc)
                    else:
                        # Handle bytes content
                        doc_content = doc
                    
                    # Extract content
                    result = self.parallel_extractor.extract_parallel(doc_content)
                    results.append({
                        "document_id": i,
                        "source": doc if isinstance(doc, str) else f"bytes_{i}",
                        "result": result,
                        "status": "success"
                    })
                    
                    # Update checkpoint
                    if (i + 1) % self.checkpoint_interval == 0:
                        self.progress_persistence.update_checkpoint(
                            operation_id, i + 1, failed_items, 
                            {"partial_results": results[-self.checkpoint_interval:]}
                        )
                    
                    # Memory optimization
                    if (i + 1) % (self.checkpoint_interval * 2) == 0:
                        gc.collect()
                    
                except Exception as e:
                    logger.error(f"Failed to process document {i}: {e}")
                    failed_items.append(f"document_{i}")
                    results.append({
                        "document_id": i,
                        "source": doc if isinstance(doc, str) else f"bytes_{i}",
                        "error": str(e),
                        "status": "failed"
                    })
            
            # Final checkpoint update
            self.progress_persistence.update_checkpoint(
                operation_id, len(documents), failed_items
            )
            
            batch_results = {
                "operation_id": operation_id,
                "total_documents": len(documents),
                "successful_documents": len(results) - len(failed_items),
                "failed_documents": len(failed_items),
                "processing_time": (datetime.now() - checkpoint.start_time).total_seconds(),
                "results": results
            }
            
            # Complete checkpoint
            self.progress_persistence.complete_checkpoint(operation_id)
            
            return batch_results
        
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            raise ProcessingError(f"Batch processing failed: {e}")
    
    def _load_document(self, source: str) -> bytes:
        """Load document from file path or URL."""
        if source.startswith(('http://', 'https://')):
            # Handle URL (this would integrate with existing URL handling)
            from .ingest import create_ingestor
            ingestor = create_ingestor(source)
            return ingestor.ingest()
        else:
            # Handle file path
            with open(source, 'rb') as f:
                return f.read()

# Global instances for easy access
_global_cache = None
_global_monitor = None
_global_parallel_extractor = None

def get_performance_cache() -> PerformanceCache:
    """Get global performance cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = PerformanceCache()
    return _global_cache

def get_resource_monitor() -> ResourceMonitor:
    """Get global resource monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ResourceMonitor()
    return _global_monitor

def get_parallel_extractor() -> ParallelExtractor:
    """Get global parallel extractor instance."""
    global _global_parallel_extractor
    if _global_parallel_extractor is None:
        _global_parallel_extractor = ParallelExtractor()
    return _global_parallel_extractor

def memory_optimized(func):
    """Decorator for memory optimization."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Force garbage collection before function
        gc.collect()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Force garbage collection after function
            gc.collect()
    
    return wrapper

def with_performance_monitoring(func):
    """Decorator to add performance monitoring to functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        monitor = get_resource_monitor()
        monitor.start_monitoring()
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            
            # Log performance metrics
            metrics = monitor.get_current_metrics()
            logger.info(f"Function {func.__name__} completed in {end_time - start_time:.2f}s")
            logger.info(f"Peak memory usage: {metrics.memory_percent:.1f}%")
            
            return result
        finally:
            monitor.stop_monitoring()
    
    return wrapper

def extract_with_full_optimization(pdf_content: bytes, enable_caching: bool = True,
                                  enable_monitoring: bool = True, 
                                  extraction_types: List[str] = None,
                                  output_format: str = None, output_path: str = None) -> Dict[str, Any]:
    """
    Extract content with full Stage 4 performance optimizations and optional output formatting.
    
    Args:
        pdf_content: PDF file as bytes
        enable_caching: Whether to use intelligent caching
        enable_monitoring: Whether to enable performance monitoring
        extraction_types: Types of extraction to perform
        output_format: Optional output format (html, latex, xml, csv, markdown)
        output_path: Optional path for formatted output
    
    Returns:
        Complete extraction results with optimizations applied
    """
    try:
        # Create optimizer with configurations
        optimizer = ExtractionOptimizer(
            enable_caching=enable_caching,
            enable_monitoring=enable_monitoring
        )
        
        # Perform optimized extraction with output formatting
        results = optimizer.extract_parallel(
            pdf_content, 
            extraction_types=extraction_types,
            output_format=output_format,
            output_path=output_path
        )
        
        logger.info("Full optimization extraction completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Optimized extraction failed: {e}")
        raise ProcessingError(f"Failed optimized extraction: {str(e)}")

def extract_with_monitoring_only(pdf_content: bytes, extraction_types: List[str] = None,
                                output_format: str = None, output_path: str = None) -> Dict[str, Any]:
    """
    Extract content with monitoring only (no caching) and optional output formatting.
    
    Args:
        pdf_content: PDF file as bytes
        extraction_types: Types of extraction to perform
        output_format: Optional output format (html, latex, xml, csv, markdown)
        output_path: Optional path for formatted output
    
    Returns:
        Extraction results with monitoring data
    """
    return extract_with_full_optimization(
        pdf_content, 
        enable_caching=False, 
        enable_monitoring=True,
        extraction_types=extraction_types,
        output_format=output_format,
        output_path=output_path
    )

def clear_all_caches():
    """Clear all performance caches."""
    global _global_cache
    if _global_cache:
        _global_cache.clear()
    logger.info("All performance caches cleared")

def get_system_recommendations() -> Dict[str, Any]:
    """Get system optimization recommendations."""
    monitor = get_resource_monitor()
    cache = get_performance_cache()
    
    recommendations = monitor.get_recommendations()
    recommendations["cache_stats"] = cache.get_cache_stats()
    
    return recommendations 
"""
Comprehensive tests for Stage 4 performance optimizations.

Tests all performance features:
- Multiprocessing for batch operations
- Memory optimization for large files
- Streaming processing for continuous data flows
- Result caching to avoid reprocessing
- Progress persistence for resumable operations
- Resource usage monitoring and reporting
- Automatic scaling based on system resources
"""

import os
import time
import tempfile
import threading
from unittest.mock import Mock, patch
from pathlib import Path
import pytest

from paper2data.performance import (
    ResourceMonitor,
    PerformanceCache,
    ParallelExtractor,
    BatchProcessor as PerformanceBatchProcessor,
    StreamingProcessor,
    ProgressPersistence,
    get_performance_cache,
    get_resource_monitor,
    get_parallel_extractor,
    extract_with_full_optimization,
    get_system_recommendations,
    clear_all_caches,
    memory_optimized,
    with_performance_monitoring,
    ResourceMetrics,
    ProcessingCheckpoint
)
from paper2data.extractor import extract_all_content_optimized


class TestResourceMonitor:
    """Test resource monitoring functionality."""
    
    def test_resource_monitor_creation(self):
        """Test ResourceMonitor instantiation."""
        monitor = ResourceMonitor()
        assert monitor.monitoring_interval == 1.0
        assert monitor.is_monitoring == False
        assert len(monitor.metrics_history) == 0
    
    def test_collect_metrics(self):
        """Test metrics collection."""
        monitor = ResourceMonitor()
        metrics = monitor.get_current_metrics()
        
        assert isinstance(metrics, ResourceMetrics)
        assert metrics.cpu_percent >= 0
        assert metrics.memory_percent >= 0
        assert metrics.memory_available > 0
        assert metrics.memory_used > 0
        assert metrics.disk_usage >= 0
        assert metrics.active_processes > 0
    
    def test_monitor_lifecycle(self):
        """Test monitoring start/stop lifecycle."""
        monitor = ResourceMonitor(monitoring_interval=0.1)
        
        # Start monitoring
        monitor.start_monitoring()
        assert monitor.is_monitoring == True
        
        # Let it collect a few metrics
        time.sleep(0.3)
        
        # Stop monitoring
        monitor.stop_monitoring()
        assert monitor.is_monitoring == False
        
        # Should have collected some metrics
        assert len(monitor.metrics_history) > 0
    
    def test_optimization_recommendations(self):
        """Test optimization recommendations."""
        monitor = ResourceMonitor()
        recommendations = monitor.get_recommendations()
        
        assert "optimal_worker_count" in recommendations
        assert "memory_optimization_needed" in recommendations
        assert "batch_size_recommendation" in recommendations
        assert "resource_warnings" in recommendations
        
        assert isinstance(recommendations["optimal_worker_count"], int)
        assert isinstance(recommendations["memory_optimization_needed"], bool)
        assert isinstance(recommendations["batch_size_recommendation"], int)
        assert isinstance(recommendations["resource_warnings"], list)


class TestPerformanceCache:
    """Test performance caching functionality."""
    
    def test_cache_creation(self):
        """Test cache instantiation."""
        cache = PerformanceCache(max_size=10, ttl=60)
        assert cache.memory_cache.maxsize == 10
        assert cache.memory_cache.ttl == 60
    
    def test_cache_operations(self):
        """Test cache set/get operations."""
        cache = PerformanceCache(max_size=10, ttl=60)
        
        # Test data
        pdf_content = b"test pdf content"
        test_result = {"test": "data", "pages": 5}
        
        # Test cache miss
        result = cache.get(pdf_content, "test_extraction")
        assert result is None
        
        # Test cache set
        cache.set(pdf_content, test_result, "test_extraction")
        
        # Test cache hit
        cached_result = cache.get(pdf_content, "test_extraction")
        assert cached_result == test_result
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = PerformanceCache(max_size=10, ttl=60)
        
        stats = cache.get_cache_stats()
        assert "memory_cache_size" in stats
        assert "memory_cache_max" in stats
        assert "disk_cache_files" in stats
        assert "disk_cache_size_mb" in stats
        assert stats["memory_cache_max"] == 10
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = PerformanceCache(max_size=10, ttl=60)
        
        # Add some data
        cache.set(b"test1", {"data": 1}, "test")
        cache.set(b"test2", {"data": 2}, "test")
        
        # Verify data exists
        assert cache.get(b"test1", "test") is not None
        assert cache.get(b"test2", "test") is not None
        
        # Clear cache
        cache.clear()
        
        # Verify data is gone
        assert cache.get(b"test1", "test") is None
        assert cache.get(b"test2", "test") is None


class TestProgressPersistence:
    """Test progress persistence functionality."""
    
    def test_checkpoint_creation(self):
        """Test checkpoint creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            persistence = ProgressPersistence(Path(temp_dir))
            
            checkpoint = persistence.create_checkpoint("test_op", 100)
            
            assert checkpoint.operation_id == "test_op"
            assert checkpoint.total_items == 100
            assert checkpoint.completed_items == 0
            assert checkpoint.failed_items == []
    
    def test_checkpoint_update(self):
        """Test checkpoint updates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            persistence = ProgressPersistence(Path(temp_dir))
            
            checkpoint = persistence.create_checkpoint("test_op", 100)
            
            # Update progress
            persistence.update_checkpoint("test_op", 50, ["failed_item1"], {"test": "data"})
            
            # Check updates
            updated_checkpoint = persistence.active_checkpoints["test_op"]
            assert updated_checkpoint.completed_items == 50
            assert "failed_item1" in updated_checkpoint.failed_items
            assert updated_checkpoint.results["test"] == "data"
    
    def test_checkpoint_persistence(self):
        """Test checkpoint save/load."""
        with tempfile.TemporaryDirectory() as temp_dir:
            persistence = ProgressPersistence(Path(temp_dir))
            
            # Create and update checkpoint
            checkpoint = persistence.create_checkpoint("test_op", 100)
            persistence.update_checkpoint("test_op", 75, ["failed1", "failed2"])
            
            # Create new persistence instance (simulate restart)
            new_persistence = ProgressPersistence(Path(temp_dir))
            
            # Load checkpoint
            loaded_checkpoint = new_persistence.load_checkpoint("test_op")
            
            assert loaded_checkpoint is not None
            assert loaded_checkpoint.operation_id == "test_op"
            assert loaded_checkpoint.total_items == 100
            assert loaded_checkpoint.completed_items == 75
            assert len(loaded_checkpoint.failed_items) == 2


class TestStreamingProcessor:
    """Test streaming processing functionality."""
    
    def test_streaming_processor_creation(self):
        """Test StreamingProcessor instantiation."""
        processor = StreamingProcessor(chunk_size=5, memory_threshold=0.9)
        assert processor.chunk_size == 5
        assert processor.memory_threshold == 0.9
    
    def test_stream_processing(self):
        """Test stream processing with small dataset."""
        processor = StreamingProcessor(chunk_size=2, memory_threshold=0.9)
        
        # Mock data stream
        data_stream = [f"item_{i}" for i in range(10)]
        
        # Mock processor function
        def mock_processor(item):
            return f"processed_{item}"
        
        # Process stream
        results = list(processor.process_stream(iter(data_stream), mock_processor))
        
        # Verify results
        assert len(results) == 10
        assert all(r.startswith("processed_") for r in results)
        assert "processed_item_0" in results
        assert "processed_item_9" in results


class TestParallelExtractor:
    """Test parallel extraction functionality."""
    
    def test_parallel_extractor_creation(self):
        """Test ParallelExtractor instantiation."""
        extractor = ParallelExtractor(max_workers=2)
        assert extractor.max_workers == 2
        assert extractor.current_workers == 2
    
    def test_parallel_extraction_with_mock_data(self):
        """Test parallel extraction with mock PDF data."""
        extractor = ParallelExtractor(max_workers=2, enable_monitoring=False)
        
        # Mock PDF content
        mock_pdf_content = b"mock pdf content for testing"
        
        # Mock the extractors to avoid actual PDF processing
        with patch('paper2data.extractor.ContentExtractor') as mock_content, \
             patch('paper2data.extractor.SectionExtractor') as mock_sections:
            
            # Configure mocks
            mock_content.return_value.extract.return_value = {"statistics": {"page_count": 5, "word_count": 1000}}
            mock_sections.return_value.extract.return_value = {"section_count": 3}
            
            # Test extraction
            results = extractor.extract_parallel(mock_pdf_content, ["content", "sections"])
            
            # Verify results structure
            assert "extraction_timestamp" in results
            assert "content" in results
            assert "sections" in results
            assert "summary" in results
            assert results["summary"]["total_pages"] == 5
            assert results["summary"]["sections_found"] == 3


class TestBatchProcessor:
    """Test batch processing functionality."""
    
    def test_batch_processor_creation(self):
        """Test BatchProcessor instantiation."""
        processor = PerformanceBatchProcessor(max_workers=2, checkpoint_interval=5)
        assert processor.checkpoint_interval == 5
    
    def test_batch_processing_with_mock_data(self):
        """Test batch processing with mock documents."""
        processor = PerformanceBatchProcessor(max_workers=1, checkpoint_interval=2)
        
        # Mock documents (using bytes to avoid file loading)
        mock_documents = [
            b"mock pdf 1 content",
            b"mock pdf 2 content",
            b"mock pdf 3 content"
        ]
        
        # Mock the parallel extractor
        with patch.object(processor.parallel_extractor, 'extract_parallel') as mock_extract:
            mock_extract.return_value = {"test": "result", "pages": 1}
            
            # Process batch
            results = processor.process_batch(mock_documents, "test_batch")
            
            # Verify results
            assert results["operation_id"] == "test_batch"
            assert results["total_documents"] == 3
            assert results["successful_documents"] == 3
            assert results["failed_documents"] == 0
            assert len(results["results"]) == 3


class TestGlobalInstances:
    """Test global instance management."""
    
    def test_global_cache_instance(self):
        """Test global cache instance."""
        cache1 = get_performance_cache()
        cache2 = get_performance_cache()
        
        # Should be the same instance
        assert cache1 is cache2
    
    def test_global_monitor_instance(self):
        """Test global monitor instance."""
        monitor1 = get_resource_monitor()
        monitor2 = get_resource_monitor()
        
        # Should be the same instance
        assert monitor1 is monitor2
    
    def test_global_extractor_instance(self):
        """Test global extractor instance."""
        extractor1 = get_parallel_extractor()
        extractor2 = get_parallel_extractor()
        
        # Should be the same instance
        assert extractor1 is extractor2
    
    def test_system_recommendations(self):
        """Test system recommendations."""
        recommendations = get_system_recommendations()
        
        assert "optimal_worker_count" in recommendations
        assert "cache_stats" in recommendations
        assert isinstance(recommendations["optimal_worker_count"], int)
        assert isinstance(recommendations["cache_stats"], dict)


class TestDecorators:
    """Test performance decorators."""
    
    def test_memory_optimized_decorator(self):
        """Test memory optimization decorator."""
        @memory_optimized
        def test_function():
            return "test result"
        
        result = test_function()
        assert result == "test result"
    
    def test_performance_monitoring_decorator(self):
        """Test performance monitoring decorator."""
        @with_performance_monitoring
        def test_function():
            time.sleep(0.1)  # Simulate some work
            return "test result"
        
        result = test_function()
        assert result == "test result"


class TestExtractorIntegration:
    """Test integration with main extractor module."""
    
    def test_optimized_extraction_fallback(self):
        """Test optimized extraction fallback to sequential."""
        # Mock PDF content
        mock_pdf_content = b"mock pdf content"
        
        # Mock the regular extract_all_content function
        with patch('paper2data.extractor.extract_all_content') as mock_extract:
            mock_extract.return_value = {"test": "result"}
            
            # Test with parallel disabled
            result = extract_all_content_optimized(mock_pdf_content, enable_parallel=False)
            
            # Should call the regular function
            assert result == {"test": "result"}
            mock_extract.assert_called_once()


class TestCacheClearing:
    """Test cache clearing functionality."""
    
    def test_clear_all_caches(self):
        """Test clearing all caches."""
        # Get cache instance and add some data
        cache = get_performance_cache()
        cache.set(b"test", {"data": "test"}, "test_type")
        
        # Verify data exists
        assert cache.get(b"test", "test_type") is not None
        
        # Clear all caches
        clear_all_caches()
        
        # Verify data is cleared
        assert cache.get(b"test", "test_type") is None


class TestResourceMetrics:
    """Test ResourceMetrics data class."""
    
    def test_resource_metrics_serialization(self):
        """Test ResourceMetrics to_dict conversion."""
        from datetime import datetime
        
        metrics = ResourceMetrics(
            timestamp=datetime.now(),
            cpu_percent=25.5,
            memory_percent=60.0,
            memory_available=1000000,
            memory_used=500000,
            disk_usage=45.0,
            active_processes=150
        )
        
        data = metrics.to_dict()
        
        assert isinstance(data["timestamp"], str)
        assert data["cpu_percent"] == 25.5
        assert data["memory_percent"] == 60.0
        assert data["memory_available"] == 1000000
        assert data["memory_used"] == 500000
        assert data["disk_usage"] == 45.0
        assert data["active_processes"] == 150


class TestProcessingCheckpoint:
    """Test ProcessingCheckpoint data class."""
    
    def test_checkpoint_serialization(self):
        """Test ProcessingCheckpoint serialization/deserialization."""
        from datetime import datetime
        
        checkpoint = ProcessingCheckpoint(
            operation_id="test_op",
            total_items=100,
            completed_items=50,
            failed_items=["item1", "item2"],
            start_time=datetime.now(),
            last_update=datetime.now(),
            results={"test": "data"}
        )
        
        # Serialize
        data = checkpoint.to_dict()
        
        # Deserialize
        restored_checkpoint = ProcessingCheckpoint.from_dict(data)
        
        assert restored_checkpoint.operation_id == checkpoint.operation_id
        assert restored_checkpoint.total_items == checkpoint.total_items
        assert restored_checkpoint.completed_items == checkpoint.completed_items
        assert restored_checkpoint.failed_items == checkpoint.failed_items
        assert restored_checkpoint.results == checkpoint.results


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
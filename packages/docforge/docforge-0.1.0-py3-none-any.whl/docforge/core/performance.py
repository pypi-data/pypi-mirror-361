# docforge/core/performance.py
"""
Advanced Performance Optimization System for DocForge
Includes multi-threading, caching, memory optimization, and resource management
"""

import asyncio
import threading
import multiprocessing
import psutil
import time
import hashlib
import pickle
import gzip
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from threading import Lock, Event
from queue import Queue, PriorityQueue
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple, Union
from dataclasses import dataclass, field
from functools import wraps, lru_cache
import weakref
import mmap
import os
import gc

from ..core.exceptions import ProcessingResult, DocForgeException
from ..cli.rich_interface import DocForgeUI


@dataclass
class PerformanceMetrics:
    """Performance metrics tracking."""

    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    cpu_usage_start: float = 0.0
    cpu_usage_end: float = 0.0
    memory_usage_start: int = 0
    memory_usage_end: int = 0
    files_processed: int = 0
    bytes_processed: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    threads_used: int = 0

    def __post_init__(self):
        """Initialize system metrics."""
        process = psutil.Process()
        self.cpu_usage_start = process.cpu_percent()
        self.memory_usage_start = process.memory_info().rss

    def finish(self):
        """Finalize metrics collection."""
        self.end_time = time.time()
        process = psutil.Process()
        self.cpu_usage_end = process.cpu_percent()
        self.memory_usage_end = process.memory_info().rss

    @property
    def duration(self) -> float:
        """Get processing duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def files_per_second(self) -> float:
        """Get files processed per second."""
        duration = self.duration
        return self.files_processed / duration if duration > 0 else 0

    @property
    def bytes_per_second(self) -> float:
        """Get bytes processed per second."""
        duration = self.duration
        return self.bytes_processed / duration if duration > 0 else 0

    @property
    def memory_delta_mb(self) -> float:
        """Get memory usage change in MB."""
        return (self.memory_usage_end - self.memory_usage_start) / 1024 / 1024

    @property
    def cache_hit_ratio(self) -> float:
        """Get cache hit ratio."""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0


class SmartCache:
    """Intelligent caching system with LRU and size-based eviction."""

    def __init__(self, max_size_mb: int = 512, max_items: int = 1000):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_items = max_items
        self.cache: Dict[str, Tuple[Any, float, int]] = {}  # key: (data, timestamp, size)
        self.access_order: List[str] = []
        self.current_size = 0
        self.lock = Lock()
        self.hits = 0
        self.misses = 0

    def _calculate_size(self, obj: Any) -> int:
        """Estimate object size in bytes."""
        try:
            return len(pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL))
        except:
            return 1024  # Default estimate

    def _evict_lru(self):
        """Evict least recently used items."""
        while (len(self.cache) >= self.max_items or
               self.current_size > self.max_size_bytes) and self.access_order:

            lru_key = self.access_order.pop(0)
            if lru_key in self.cache:
                _, _, size = self.cache.pop(lru_key)
                self.current_size -= size

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self.lock:
            if key in self.cache:
                data, _, size = self.cache[key]
                # Update access order
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                # Update timestamp
                self.cache[key] = (data, time.time(), size)
                self.hits += 1
                return data
            else:
                self.misses += 1
                return None

    def put(self, key: str, value: Any):
        """Put item in cache."""
        with self.lock:
            size = self._calculate_size(value)

            # Don't cache if item is too large
            if size > self.max_size_bytes // 2:
                return

            # Remove existing item if present
            if key in self.cache:
                _, _, old_size = self.cache[key]
                self.current_size -= old_size
                self.access_order.remove(key)

            # Evict items if necessary
            self.current_size += size
            self._evict_lru()

            # Add new item
            self.cache[key] = (value, time.time(), size)
            self.access_order.append(key)

    def clear(self):
        """Clear cache."""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.current_size = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_ratio = self.hits / total_requests if total_requests > 0 else 0

            return {
                'items': len(self.cache),
                'size_mb': self.current_size / 1024 / 1024,
                'max_size_mb': self.max_size_bytes / 1024 / 1024,
                'hits': self.hits,
                'misses': self.misses,
                'hit_ratio': hit_ratio,
                'utilization': len(self.cache) / self.max_items
            }


class MemoryMappedFileProcessor:
    """Memory-mapped file processing for large PDFs."""

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.file_size = self.file_path.stat().st_size
        self.mmap_obj = None
        self.file_obj = None

    def __enter__(self):
        """Enter context manager."""
        self.file_obj = open(self.file_path, 'rb')
        self.mmap_obj = mmap.mmap(self.file_obj.fileno(), 0, access=mmap.ACCESS_READ)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self.mmap_obj:
            self.mmap_obj.close()
        if self.file_obj:
            self.file_obj.close()

    def read_chunk(self, offset: int, size: int) -> bytes:
        """Read a chunk of the file."""
        if not self.mmap_obj:
            raise RuntimeError("File not opened")

        end_pos = min(offset + size, self.file_size)
        return self.mmap_obj[offset:end_pos]

    def find_pattern(self, pattern: bytes, start: int = 0) -> int:
        """Find pattern in memory-mapped file."""
        if not self.mmap_obj:
            raise RuntimeError("File not opened")

        return self.mmap_obj.find(pattern, start)


class ResourceMonitor:
    """Real-time resource monitoring and throttling."""

    def __init__(self, max_cpu_percent: float = 80.0, max_memory_mb: int = 2048):
        self.max_cpu_percent = max_cpu_percent
        self.max_memory_mb = max_memory_mb
        self.monitoring = False
        self.monitor_thread = None
        self.throttle_event = Event()
        self.throttle_event.set()  # Start unthrottled

    def start_monitoring(self):
        """Start resource monitoring."""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop resource monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)

    def _monitor_loop(self):
        """Resource monitoring loop."""
        process = psutil.Process()

        while self.monitoring:
            try:
                # Check CPU usage
                cpu_percent = process.cpu_percent(interval=1.0)

                # Check memory usage
                memory_mb = process.memory_info().rss / 1024 / 1024

                # Throttle if resources are high
                should_throttle = (
                        cpu_percent > self.max_cpu_percent or
                        memory_mb > self.max_memory_mb
                )

                if should_throttle:
                    self.throttle_event.clear()
                    time.sleep(2.0)  # Wait before checking again
                else:
                    self.throttle_event.set()

            except Exception:
                # Continue monitoring even if there's an error
                time.sleep(1.0)

    def wait_if_throttled(self):
        """Wait if system is being throttled."""
        self.throttle_event.wait()

    def get_current_usage(self) -> Dict[str, float]:
        """Get current resource usage."""
        process = psutil.Process()
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'memory_percent': process.memory_percent()
        }


class SmartThreadPool:
    """Intelligent thread pool with adaptive sizing and load balancing."""

    def __init__(self, initial_workers: Optional[int] = None, max_workers: Optional[int] = None):
        self.initial_workers = initial_workers or min(4, multiprocessing.cpu_count())
        self.max_workers = max_workers or multiprocessing.cpu_count() * 2
        self.current_workers = self.initial_workers

        self.executor = ThreadPoolExecutor(max_workers=self.current_workers)
        self.task_queue = PriorityQueue()
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.total_processing_time = 0.0

        self.lock = Lock()
        self.resource_monitor = ResourceMonitor()
        self.resource_monitor.start_monitoring()

    def submit_task(self, func: Callable, *args, priority: int = 0, **kwargs):
        """Submit a task with priority."""
        task_id = id(func) + hash(args) + hash(tuple(kwargs.items()))

        # Wrap function with timing and resource monitoring
        def wrapped_func():
            self.resource_monitor.wait_if_throttled()
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                with self.lock:
                    self.completed_tasks += 1
                    self.total_processing_time += duration

                return result
            except Exception as e:
                with self.lock:
                    self.failed_tasks += 1
                raise e

        return self.executor.submit(wrapped_func)

    def adaptive_resize(self):
        """Adaptively resize thread pool based on performance."""
        with self.lock:
            if self.completed_tasks < 10:
                return  # Not enough data

            avg_task_time = self.total_processing_time / self.completed_tasks
            failure_rate = self.failed_tasks / (self.completed_tasks + self.failed_tasks)

            # Get current resource usage
            usage = self.resource_monitor.get_current_usage()

            # Decide whether to scale up or down
            if (avg_task_time < 1.0 and
                    failure_rate < 0.1 and
                    usage['cpu_percent'] < 60 and
                    self.current_workers < self.max_workers):
                # Scale up
                self.current_workers = min(self.current_workers + 1, self.max_workers)
                self._recreate_executor()

            elif (avg_task_time > 5.0 or
                  failure_rate > 0.2 or
                  usage['cpu_percent'] > 80):
                # Scale down
                self.current_workers = max(self.current_workers - 1, 1)
                self._recreate_executor()

    def _recreate_executor(self):
        """Recreate executor with new worker count."""
        old_executor = self.executor
        self.executor = ThreadPoolExecutor(max_workers=self.current_workers)
        old_executor.shutdown(wait=False)

    def shutdown(self):
        """Shutdown thread pool."""
        self.executor.shutdown(wait=True)
        self.resource_monitor.stop_monitoring()

    def get_stats(self) -> Dict[str, Any]:
        """Get thread pool statistics."""
        with self.lock:
            total_tasks = self.completed_tasks + self.failed_tasks
            success_rate = self.completed_tasks / total_tasks if total_tasks > 0 else 0
            avg_time = self.total_processing_time / self.completed_tasks if self.completed_tasks > 0 else 0

            return {
                'current_workers': self.current_workers,
                'max_workers': self.max_workers,
                'completed_tasks': self.completed_tasks,
                'failed_tasks': self.failed_tasks,
                'success_rate': success_rate,
                'avg_processing_time': avg_time,
                'resource_usage': self.resource_monitor.get_current_usage()
            }


class PerformanceOptimizer:
    """Main performance optimization coordinator."""

    def __init__(self, ui: Optional[DocForgeUI] = None):
        self.ui = ui
        self.cache = SmartCache()
        self.thread_pool = SmartThreadPool()
        self.metrics = PerformanceMetrics()

        # Performance settings
        self.enable_caching = True
        self.enable_memory_mapping = True
        self.enable_adaptive_threading = True
        self.chunk_size = 8192  # 8KB chunks for file processing

    def optimize_batch_processing(self,
                                  files: List[Path],
                                  processor_func: Callable,
                                  **kwargs) -> List[ProcessingResult]:
        """Optimized batch processing with all performance features."""

        if self.ui:
            self.ui.print_info(f"🚀 Starting optimized batch processing of {len(files)} files")

        # Reset metrics
        self.metrics = PerformanceMetrics()
        self.metrics.files_processed = len(files)
        self.metrics.bytes_processed = sum(f.stat().st_size for f in files if f.exists())

        # Group files by size for optimal batching
        small_files = [f for f in files if f.stat().st_size < 10 * 1024 * 1024]  # < 10MB
        large_files = [f for f in files if f.stat().st_size >= 10 * 1024 * 1024]  # >= 10MB

        results = []

        # Process small files with high concurrency
        if small_files:
            if self.ui:
                self.ui.print_info(f"⚡ Processing {len(small_files)} small files with high concurrency")

            small_results = self._process_files_concurrent(
                small_files, processor_func, high_concurrency=True, **kwargs
            )
            results.extend(small_results)

        # Process large files with memory optimization
        if large_files:
            if self.ui:
                self.ui.print_info(f"🧠 Processing {len(large_files)} large files with memory optimization")

            large_results = self._process_files_memory_optimized(
                large_files, processor_func, **kwargs
            )
            results.extend(large_results)

        # Finalize metrics
        self.metrics.finish()

        if self.ui:
            self._display_performance_summary()

        return results

    def _process_files_concurrent(self,
                                  files: List[Path],
                                  processor_func: Callable,
                                  high_concurrency: bool = False,
                                  **kwargs) -> List[ProcessingResult]:
        """Process files with high concurrency."""

        max_workers = self.thread_pool.max_workers if high_concurrency else self.thread_pool.current_workers

        futures = []
        for file_path in files:
            future = self.thread_pool.submit_task(
                self._process_single_file_cached,
                file_path, processor_func, **kwargs
            )
            futures.append((file_path, future))

        results = []
        for file_path, future in futures:
            try:
                result = future.result(timeout=300)  # 5 minute timeout
                results.append(result)

                # Adaptive thread pool resizing
                if self.enable_adaptive_threading:
                    self.thread_pool.adaptive_resize()

            except Exception as e:
                error_result = ProcessingResult.error_result(
                    DocForgeException(f"Failed to process {file_path}: {str(e)}"),
                    "Batch Processing"
                )
                results.append(error_result)

        return results

    def _process_files_memory_optimized(self,
                                        files: List[Path],
                                        processor_func: Callable,
                                        **kwargs) -> List[ProcessingResult]:
        """Process large files with memory optimization."""

        results = []

        for file_path in files:
            # Force garbage collection before processing large files
            gc.collect()

            try:
                if self.enable_memory_mapping and file_path.suffix.lower() == '.pdf':
                    result = self._process_file_memory_mapped(file_path, processor_func, **kwargs)
                else:
                    result = self._process_single_file_cached(file_path, processor_func, **kwargs)

                results.append(result)

            except Exception as e:
                error_result = ProcessingResult.error_result(
                    DocForgeException(f"Failed to process {file_path}: {str(e)}"),
                    "Memory Optimized Processing"
                )
                results.append(error_result)

            # Brief pause to allow system recovery
            time.sleep(0.1)

        return results

    def _process_single_file_cached(self,
                                    file_path: Path,
                                    processor_func: Callable,
                                    **kwargs) -> ProcessingResult:
        """Process single file with caching."""

        # Generate cache key based on file and parameters
        file_stat = file_path.stat()
        cache_key = hashlib.md5(
            f"{file_path}:{file_stat.st_mtime}:{file_stat.st_size}:{kwargs}".encode()
        ).hexdigest()

        # Check cache first
        if self.enable_caching:
            cached_result = self.cache.get(cache_key)
            if cached_result:
                self.metrics.cache_hits += 1
                return cached_result

        self.metrics.cache_misses += 1

        # Process file
        start_time = time.time()
        result = processor_func(file_path, **kwargs)
        processing_time = time.time() - start_time

        # Cache successful results
        if self.enable_caching and isinstance(result, ProcessingResult) and result.success:
            self.cache.put(cache_key, result)

        return result

    def _process_file_memory_mapped(self,
                                    file_path: Path,
                                    processor_func: Callable,
                                    **kwargs) -> ProcessingResult:
        """Process file using memory mapping."""

        with MemoryMappedFileProcessor(file_path) as mmap_processor:
            # Enhanced processing with memory mapping
            return processor_func(file_path, mmap_processor=mmap_processor, **kwargs)

    def _display_performance_summary(self):
        """Display comprehensive performance summary."""
        if not self.ui:
            return

        # Get statistics
        cache_stats = self.cache.get_stats()
        thread_stats = self.thread_pool.get_stats()

        # Create performance summary
        summary_data = [
            ["📊 Files Processed", f"{self.metrics.files_processed:,}"],
            ["⚡ Files/Second", f"{self.metrics.files_per_second:.2f}"],
            ["💾 Data Processed", f"{self.metrics.bytes_processed / 1024 / 1024:.1f} MB"],
            ["🚀 MB/Second", f"{self.metrics.bytes_per_second / 1024 / 1024:.2f}"],
            ["⏱️ Total Time", f"{self.metrics.duration:.2f}s"],
            ["💻 Memory Delta", f"{self.metrics.memory_delta_mb:+.1f} MB"],
            ["🧵 Threads Used", f"{thread_stats['current_workers']}"],
            ["✅ Success Rate", f"{thread_stats['success_rate']:.1%}"],
            ["🗄️ Cache Hit Ratio", f"{cache_stats['hit_ratio']:.1%}"],
            ["📈 Cache Utilization", f"{cache_stats['utilization']:.1%}"],
        ]

        # Display as table
        from rich.table import Table
        from rich import box

        table = Table(title="🚀 Performance Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="yellow", justify="right")

        for metric, value in summary_data:
            table.add_row(metric, value)

        self.ui.console.print(table)

        # Performance recommendations
        recommendations = self._generate_performance_recommendations(cache_stats, thread_stats)
        if recommendations:
            self.ui.display_suggestions_panel("🚀 Performance Recommendations", recommendations)

    def _generate_performance_recommendations(self,
                                              cache_stats: Dict,
                                              thread_stats: Dict) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []

        # Cache recommendations
        if cache_stats['hit_ratio'] < 0.3:
            recommendations.append("Consider increasing cache size for better performance")

        if cache_stats['utilization'] > 0.9:
            recommendations.append("Cache is nearly full - consider increasing max_items")

        # Thread recommendations
        if thread_stats['success_rate'] < 0.95:
            recommendations.append("High failure rate detected - check system resources")

        if thread_stats['avg_processing_time'] > 10.0:
            recommendations.append("Long processing times - consider smaller batch sizes")

        # Resource recommendations
        usage = thread_stats['resource_usage']
        if usage['cpu_percent'] > 90:
            recommendations.append("High CPU usage - consider reducing thread count")

        if usage['memory_mb'] > 4000:
            recommendations.append("High memory usage - enable memory mapping for large files")

        # Performance achievements
        if self.metrics.files_per_second > 10:
            recommendations.append("🎉 Excellent processing speed achieved!")

        if cache_stats['hit_ratio'] > 0.7:
            recommendations.append("🎉 Great cache performance!")

        return recommendations

    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            'metrics': {
                'duration': self.metrics.duration,
                'files_processed': self.metrics.files_processed,
                'files_per_second': self.metrics.files_per_second,
                'bytes_processed': self.metrics.bytes_processed,
                'bytes_per_second': self.metrics.bytes_per_second,
                'memory_delta_mb': self.metrics.memory_delta_mb,
                'cache_hit_ratio': self.metrics.cache_hit_ratio
            },
            'cache_stats': self.cache.get_stats(),
            'thread_stats': self.thread_pool.get_stats(),
            'timestamp': time.time()
        }

    def cleanup(self):
        """Cleanup resources."""
        self.thread_pool.shutdown()
        self.cache.clear()


# Performance decorators
def performance_monitor(func):
    """Decorator to monitor function performance."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        try:
            result = func(*args, **kwargs)

            # Add performance info to result if it's a ProcessingResult
            if isinstance(result, ProcessingResult):
                duration = time.time() - start_time
                memory_delta = psutil.Process().memory_info().rss - start_memory

                if not result.metadata:
                    result.metadata = {}

                result.metadata.update({
                    'performance': {
                        'duration': duration,
                        'memory_delta_mb': memory_delta / 1024 / 1024,
                        'function': func.__name__
                    }
                })

            return result

        except Exception as e:
            duration = time.time() - start_time
            # Log performance even for failed operations
            print(f"Function {func.__name__} failed after {duration:.2f}s: {e}")
            raise

    return wrapper


def memory_efficient(chunk_size: int = 8192):
    """Decorator for memory-efficient file processing."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Force garbage collection before processing
            gc.collect()

            # Add chunk_size to kwargs if not present
            if 'chunk_size' not in kwargs:
                kwargs['chunk_size'] = chunk_size

            try:
                return func(*args, **kwargs)
            finally:
                # Force garbage collection after processing
                gc.collect()

        return wrapper

    return decorator

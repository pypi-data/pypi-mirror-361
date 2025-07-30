import gc
import psutil
import threading
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

class PerformanceMonitor:
    """System performance monitoring and optimization"""
    
    def __init__(self, memory_limit_mb: int = 512):
        self.memory_limit_mb = memory_limit_mb
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self._stats = {
            'function_calls': {},
            'memory_usage': [],
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
    
    def check_memory_limit(self) -> bool:
        """Check if memory usage exceeds limit"""
        current_usage = self.get_memory_usage()
        return current_usage['rss_mb'] > self.memory_limit_mb
    
    def optimize_memory(self) -> Dict[str, Any]:
        """Perform memory optimization"""
        before_usage = self.get_memory_usage()
        
        # Force garbage collection
        collected = gc.collect()
        
        # Clear unreferenced objects
        gc.set_threshold(700, 10, 10)
        
        after_usage = self.get_memory_usage()
        
        return {
            'objects_collected': collected,
            'memory_freed_mb': before_usage['rss_mb'] - after_usage['rss_mb'],
            'before_mb': before_usage['rss_mb'],
            'after_mb': after_usage['rss_mb']
        }
    
    def record_function_call(self, func_name: str, duration: float):
        """Record function call statistics"""
        if func_name not in self._stats['function_calls']:
            self._stats['function_calls'][func_name] = {
                'count': 0,
                'total_time': 0.0,
                'avg_time': 0.0
            }
        
        stats = self._stats['function_calls'][func_name]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['avg_time'] = stats['total_time'] / stats['count']
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        return {
            'memory': self.get_memory_usage(),
            'function_calls': self._stats['function_calls'],
            'cache_hit_rate': self._stats['cache_hits'] / max(1, self._stats['cache_hits'] + self._stats['cache_misses']),
            'total_cache_operations': self._stats['cache_hits'] + self._stats['cache_misses']
        }

def performance_monitor(monitor: PerformanceMonitor):
    """Decorator to monitor function performance"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                monitor.record_function_call(func.__name__, duration)
        
        return wrapper
    return decorator

class LazyLoader:
    """Lazy loading system for modules and resources"""
    
    def __init__(self):
        self._loaded_modules = {}
        self._loading_lock = threading.Lock()
    
    def load_module(self, module_name: str, loader_func: Callable) -> Any:
        """Load module lazily with thread safety"""
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]
        
        with self._loading_lock:
            # Double-check pattern
            if module_name in self._loaded_modules:
                return self._loaded_modules[module_name]
            
            module = loader_func()
            self._loaded_modules[module_name] = module
            return module
    
    def unload_module(self, module_name: str) -> bool:
        """Unload module to free memory"""
        with self._loading_lock:
            if module_name in self._loaded_modules:
                del self._loaded_modules[module_name]
                return True
            return False
    
    def get_loaded_modules(self) -> list:
        """Get list of loaded modules"""
        return list(self._loaded_modules.keys())

class ConcurrentProcessor:
    """Concurrent processing for CPU-intensive tasks"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    def process_batch(self, items: list, processor_func: Callable, **kwargs) -> list:
        """Process items concurrently"""
        if len(items) <= 1:
            return [processor_func(item, **kwargs) for item in items]
        
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(processor_func, item, **kwargs): item 
                for item in items
            }
            
            # Collect results in order
            for future in as_completed(future_to_item):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Log error but continue processing
                    results.append(None)
        
        return results
    
    def process_with_timeout(self, func: Callable, timeout: float = 30.0, *args, **kwargs) -> Any:
        """Execute function with timeout"""
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args, **kwargs)
            try:
                return future.result(timeout=timeout)
            except Exception:
                return None

class ResourcePool:
    """Resource pooling for expensive objects"""
    
    def __init__(self, factory_func: Callable, max_size: int = 10):
        self.factory_func = factory_func
        self.max_size = max_size
        self._pool = []
        self._lock = threading.Lock()
    
    def acquire(self) -> Any:
        """Acquire resource from pool"""
        with self._lock:
            if self._pool:
                return self._pool.pop()
            else:
                return self.factory_func()
    
    def release(self, resource: Any) -> None:
        """Release resource back to pool"""
        with self._lock:
            if len(self._pool) < self.max_size:
                self._pool.append(resource)
    
    def clear(self) -> None:
        """Clear all pooled resources"""
        with self._lock:
            self._pool.clear()
    
    def size(self) -> int:
        """Get current pool size"""
        with self._lock:
            return len(self._pool)
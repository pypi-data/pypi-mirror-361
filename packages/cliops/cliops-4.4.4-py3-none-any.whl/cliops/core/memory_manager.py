import gc
import weakref
import threading
from typing import Any, Dict, Optional, Set
from collections import defaultdict

class MemoryManager:
    """Advanced memory management for CliOps"""
    
    def __init__(self, max_cache_size: int = 100):
        self.max_cache_size = max_cache_size
        self._object_registry: Dict[str, Set[weakref.ref]] = defaultdict(set)
        self._cache_usage = {}
        self._lock = threading.Lock()
    
    def register_object(self, obj: Any, category: str = 'general') -> None:
        """Register object for memory tracking"""
        with self._lock:
            weak_ref = weakref.ref(obj, self._cleanup_callback(category))
            self._object_registry[category].add(weak_ref)
    
    def _cleanup_callback(self, category: str):
        """Callback for when weakly referenced object is garbage collected"""
        def callback(weak_ref):
            with self._lock:
                self._object_registry[category].discard(weak_ref)
        return callback
    
    def get_object_count(self, category: str = None) -> int:
        """Get count of tracked objects"""
        with self._lock:
            if category:
                return len([ref for ref in self._object_registry[category] if ref() is not None])
            else:
                return sum(len([ref for ref in refs if ref() is not None]) 
                          for refs in self._object_registry.values())
    
    def cleanup_category(self, category: str) -> int:
        """Force cleanup of objects in category"""
        with self._lock:
            count = 0
            refs_to_remove = []
            
            for ref in self._object_registry[category]:
                obj = ref()
                if obj is None:
                    refs_to_remove.append(ref)
                    count += 1
            
            for ref in refs_to_remove:
                self._object_registry[category].discard(ref)
            
            return count
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """Force garbage collection and return statistics"""
        # Clean up weak references first
        total_cleaned = 0
        for category in list(self._object_registry.keys()):
            total_cleaned += self.cleanup_category(category)
        
        # Force garbage collection
        collected_gen0 = gc.collect(0)
        collected_gen1 = gc.collect(1) 
        collected_gen2 = gc.collect(2)
        
        return {
            'weak_refs_cleaned': total_cleaned,
            'gc_gen0_collected': collected_gen0,
            'gc_gen1_collected': collected_gen1,
            'gc_gen2_collected': collected_gen2,
            'total_collected': collected_gen0 + collected_gen1 + collected_gen2
        }
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        with self._lock:
            stats = {
                'tracked_objects': {},
                'total_tracked': 0,
                'gc_stats': {
                    'counts': gc.get_count(),
                    'thresholds': gc.get_threshold()
                }
            }
            
            for category, refs in self._object_registry.items():
                alive_count = len([ref for ref in refs if ref() is not None])
                stats['tracked_objects'][category] = alive_count
                stats['total_tracked'] += alive_count
            
            return stats

class ObjectPool:
    """Generic object pool for expensive-to-create objects"""
    
    def __init__(self, factory_func, max_size: int = 10, cleanup_func=None):
        self.factory_func = factory_func
        self.cleanup_func = cleanup_func
        self.max_size = max_size
        self._pool = []
        self._lock = threading.Lock()
        self._created_count = 0
        self._acquired_count = 0
        self._released_count = 0
    
    def acquire(self) -> Any:
        """Acquire object from pool or create new one"""
        with self._lock:
            if self._pool:
                obj = self._pool.pop()
                self._acquired_count += 1
                return obj
            else:
                obj = self.factory_func()
                self._created_count += 1
                self._acquired_count += 1
                return obj
    
    def release(self, obj: Any) -> None:
        """Release object back to pool"""
        with self._lock:
            if len(self._pool) < self.max_size:
                if self.cleanup_func:
                    self.cleanup_func(obj)
                self._pool.append(obj)
                self._released_count += 1
            else:
                # Pool is full, let object be garbage collected
                self._released_count += 1
    
    def clear(self) -> None:
        """Clear all objects from pool"""
        with self._lock:
            if self.cleanup_func:
                for obj in self._pool:
                    self.cleanup_func(obj)
            self._pool.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics"""
        with self._lock:
            return {
                'pool_size': len(self._pool),
                'max_size': self.max_size,
                'created_count': self._created_count,
                'acquired_count': self._acquired_count,
                'released_count': self._released_count,
                'hit_rate': self._released_count / max(1, self._acquired_count)
            }

class SmartCache:
    """Memory-aware cache with automatic cleanup"""
    
    def __init__(self, max_size: int = 1000, memory_threshold_mb: int = 100):
        self.max_size = max_size
        self.memory_threshold_mb = memory_threshold_mb
        self._cache: Dict[str, Any] = {}
        self._access_order = []
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        with self._lock:
            if key in self._cache:
                # Move to end (most recently used)
                self._access_order.remove(key)
                self._access_order.append(key)
                self._hits += 1
                return self._cache[key]
            else:
                self._misses += 1
                return default
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache with automatic cleanup"""
        with self._lock:
            # Check if we need to evict
            if len(self._cache) >= self.max_size:
                self._evict_lru()
            
            # Add/update value
            if key in self._cache:
                self._access_order.remove(key)
            else:
                self._cache[key] = value
            
            self._access_order.append(key)
    
    def _evict_lru(self) -> None:
        """Evict least recently used items"""
        if self._access_order:
            lru_key = self._access_order.pop(0)
            del self._cache[lru_key]
    
    def clear(self) -> None:
        """Clear entire cache"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': self._hits / max(1, total_requests),
                'memory_usage_estimate_kb': len(str(self._cache)) / 1024
            }
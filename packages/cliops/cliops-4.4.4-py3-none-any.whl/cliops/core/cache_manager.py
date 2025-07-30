import json
import time
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict
from .config import Config

class CacheManager:
    """High-performance caching system for CliOps"""
    
    def __init__(self, ttl: int = 3600):
        self.cache_dir = Config.get_app_data_dir() / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self._memory_cache: Dict[str, Dict] = {}
    
    def _get_cache_key(self, namespace: str, key: str) -> str:
        """Generate cache key with namespace"""
        combined = f"{namespace}:{key}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.json"
    
    def set(self, namespace: str, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cache value with optional TTL"""
        cache_key = self._get_cache_key(namespace, key)
        cache_ttl = ttl or self.ttl
        
        cache_data = {
            'value': value,
            'timestamp': time.time(),
            'ttl': cache_ttl
        }
        
        # Memory cache
        self._memory_cache[cache_key] = cache_data
        
        # Disk cache
        cache_file = self._get_cache_file(cache_key)
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except (OSError, json.JSONEncodeError):
            pass  # Fail silently for cache errors
    
    def get(self, namespace: str, key: str, default: Any = None) -> Any:
        """Get cache value"""
        cache_key = self._get_cache_key(namespace, key)
        
        # Try memory cache first
        if cache_key in self._memory_cache:
            cache_data = self._memory_cache[cache_key]
            if self._is_valid(cache_data):
                return cache_data['value']
            else:
                del self._memory_cache[cache_key]
        
        # Try disk cache
        cache_file = self._get_cache_file(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                if self._is_valid(cache_data):
                    # Restore to memory cache
                    self._memory_cache[cache_key] = cache_data
                    return cache_data['value']
                else:
                    cache_file.unlink(missing_ok=True)
            except (OSError, json.JSONDecodeError):
                pass
        
        return default
    
    def _is_valid(self, cache_data: Dict) -> bool:
        """Check if cache data is still valid"""
        if 'timestamp' not in cache_data or 'ttl' not in cache_data:
            return False
        
        age = time.time() - cache_data['timestamp']
        return age < cache_data['ttl']
    
    def invalidate(self, namespace: str, key: Optional[str] = None) -> None:
        """Invalidate cache entries"""
        if key:
            # Invalidate specific key
            cache_key = self._get_cache_key(namespace, key)
            self._memory_cache.pop(cache_key, None)
            cache_file = self._get_cache_file(cache_key)
            cache_file.unlink(missing_ok=True)
        else:
            # Invalidate entire namespace
            to_remove = []
            for cache_key in self._memory_cache:
                if cache_key.startswith(f"{namespace}:"):
                    to_remove.append(cache_key)
                    cache_file = self._get_cache_file(cache_key)
                    cache_file.unlink(missing_ok=True)
            
            for cache_key in to_remove:
                del self._memory_cache[cache_key]
    
    def clear_all(self) -> None:
        """Clear all cache"""
        self._memory_cache.clear()
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink(missing_ok=True)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        memory_count = len(self._memory_cache)
        disk_count = len(list(self.cache_dir.glob('*.json')))
        
        return {
            'memory_entries': memory_count,
            'disk_entries': disk_count,
            'cache_dir_size_mb': sum(f.stat().st_size for f in self.cache_dir.glob('*.json')) / (1024 * 1024)
        }
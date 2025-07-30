"""
Memory Cache - Fast-access, short-term memory for active tasks.

This module provides a high-performance memory cache for storing and retrieving
task-related data with efficient eviction policies and thread-safe operations.
"""

import threading
import time
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple, Union
import hashlib
import json
import weakref


class CacheEntry:
    """
    A single cache entry with metadata.
    """
    
    def __init__(self, key: str, value: Any, ttl: Optional[float] = None, 
                 priority: int = 0, tags: Optional[List[str]] = None):
        self.key = key
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.access_count = 0
        self.ttl = ttl
        self.priority = priority
        self.tags = tags or []
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl
    
    def touch(self):
        """Update the last accessed time and increment access count."""
        self.last_accessed = time.time()
        self.access_count += 1
    
    def age(self) -> float:
        """Get the age of the entry in seconds."""
        return time.time() - self.created_at


class MemoryCache:
    """
    High-performance memory cache with multiple eviction policies.
    
    Features:
    - Thread-safe operations
    - Multiple eviction policies (LRU, LFU, TTL)
    - Priority-based storage
    - Tag-based cache management
    - Statistics tracking
    - Memory usage monitoring
    """
    
    def __init__(self, 
                 max_size: int = 1000,
                 default_ttl: Optional[float] = None,
                 eviction_policy: str = "lru",
                 cleanup_interval: float = 60.0):
        """
        Initialize the memory cache.
        
        Args:
            max_size: Maximum number of entries in the cache
            default_ttl: Default time-to-live for entries (seconds)
            eviction_policy: Eviction policy ("lru", "lfu", "ttl", "priority")
            cleanup_interval: Interval for automatic cleanup (seconds)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.eviction_policy = eviction_policy
        self.cleanup_interval = cleanup_interval
        
        # Thread-safe storage
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        
        # Tag tracking
        self._tags: Dict[str, set] = {}
        
        # Statistics
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
            "total_gets": 0,
            "total_sets": 0,
        }
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found/expired
        """
        with self._lock:
            self._stats["total_gets"] += 1
            
            entry = self._cache.get(key)
            if entry is None:
                self._stats["misses"] += 1
                return None
            
            # Check if expired
            if entry.is_expired():
                self._remove_entry(key)
                self._stats["misses"] += 1
                self._stats["expirations"] += 1
                return None
            
            # Update access info
            entry.touch()
            
            # Move to end for LRU
            if self.eviction_policy == "lru":
                self._cache.move_to_end(key)
            
            self._stats["hits"] += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None, 
            priority: int = 0, tags: Optional[List[str]] = None) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to store
            ttl: Time-to-live for this entry (overrides default)
            priority: Priority for eviction (higher = keep longer)
            tags: Tags for grouping/bulk operations
            
        Returns:
            True if successfully stored
        """
        with self._lock:
            self._stats["total_sets"] += 1
            
            # Remove existing entry if present
            if key in self._cache:
                self._remove_entry(key)
            
            # Check if we need to evict
            if len(self._cache) >= self.max_size:
                self._evict()
            
            # Create new entry
            entry_ttl = ttl if ttl is not None else self.default_ttl
            entry = CacheEntry(key, value, entry_ttl, priority, tags)
            
            # Store entry
            self._cache[key] = entry
            
            # Update tag tracking
            if tags:
                for tag in tags:
                    if tag not in self._tags:
                        self._tags[tag] = set()
                    self._tags[tag].add(key)
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete a specific key from the cache.
        
        Args:
            key: The cache key to delete
            
        Returns:
            True if the key was found and deleted
        """
        with self._lock:
            if key in self._cache:
                self._remove_entry(key)
                return True
            return False
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self._lock:
            self._cache.clear()
            self._tags.clear()
    
    def clear_by_tag(self, tag: str) -> int:
        """
        Clear all entries with a specific tag.
        
        Args:
            tag: The tag to clear
            
        Returns:
            Number of entries cleared
        """
        with self._lock:
            if tag not in self._tags:
                return 0
            
            keys_to_remove = list(self._tags[tag])
            for key in keys_to_remove:
                self._remove_entry(key)
            
            return len(keys_to_remove)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            hit_rate = (self._stats["hits"] / max(1, self._stats["total_gets"])) * 100
            
            return {
                **self._stats,
                "hit_rate": hit_rate,
                "current_size": len(self._cache),
                "max_size": self.max_size,
                "fill_percentage": (len(self._cache) / self.max_size) * 100,
                "total_tags": len(self._tags),
            }
    
    def get_keys(self) -> List[str]:
        """Get all cache keys."""
        with self._lock:
            return list(self._cache.keys())
    
    def get_tags(self) -> List[str]:
        """Get all cache tags."""
        with self._lock:
            return list(self._tags.keys())
    
    def get_keys_by_tag(self, tag: str) -> List[str]:
        """Get all keys with a specific tag."""
        with self._lock:
            return list(self._tags.get(tag, set()))
    
    def contains(self, key: str) -> bool:
        """Check if a key exists in the cache (and is not expired)."""
        return self.get(key) is not None
    
    def size(self) -> int:
        """Get the current number of entries in the cache."""
        with self._lock:
            return len(self._cache)
    
    def _remove_entry(self, key: str) -> None:
        """Remove an entry and update tag tracking."""
        if key not in self._cache:
            return
        
        entry = self._cache[key]
        
        # Remove from tag tracking
        for tag in entry.tags:
            if tag in self._tags:
                self._tags[tag].discard(key)
                if not self._tags[tag]:
                    del self._tags[tag]
        
        # Remove from cache
        del self._cache[key]
    
    def _evict(self) -> None:
        """Evict entries based on the eviction policy."""
        if not self._cache:
            return
        
        if self.eviction_policy == "lru":
            # Remove least recently used (first in OrderedDict)
            key = next(iter(self._cache))
            self._remove_entry(key)
        
        elif self.eviction_policy == "lfu":
            # Remove least frequently used
            min_count = min(entry.access_count for entry in self._cache.values())
            for key, entry in self._cache.items():
                if entry.access_count == min_count:
                    self._remove_entry(key)
                    break
        
        elif self.eviction_policy == "ttl":
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k].created_at)
            self._remove_entry(oldest_key)
        
        elif self.eviction_policy == "priority":
            # Remove lowest priority entry
            min_priority = min(entry.priority for entry in self._cache.values())
            for key, entry in self._cache.items():
                if entry.priority == min_priority:
                    self._remove_entry(key)
                    break
        
        self._stats["evictions"] += 1
    
    def _cleanup_worker(self) -> None:
        """Background thread for cleaning up expired entries."""
        while True:
            time.sleep(self.cleanup_interval)
            self._cleanup_expired()
    
    def _cleanup_expired(self) -> None:
        """Remove all expired entries."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                self._remove_entry(key)
                self._stats["expirations"] += 1
    
    def __len__(self) -> int:
        """Get the current number of entries in the cache."""
        return self.size()
    
    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        return self.contains(key)
    
    def __getitem__(self, key: str) -> Any:
        """Get a value from the cache (raises KeyError if not found)."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set a value in the cache."""
        self.set(key, value)
    
    def __delitem__(self, key: str) -> None:
        """Delete a key from the cache."""
        if not self.delete(key):
            raise KeyError(key) 
"""
Intelligent caching system for the aget streaming proxy.

This module provides a comprehensive caching system with TTL, size limits,
LRU eviction, and automatic cleanup for streaming media segments.
"""

import asyncio
import hashlib
import json
import os
import time
import threading
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List
import logging
from dataclasses import dataclass, asdict

from .streaming_config import CacheConfig


@dataclass
class CacheEntry:
    """Represents a cached file entry with metadata."""
    
    file_path: str
    url: str
    size: int
    created_at: float
    last_accessed: float
    access_count: int
    content_type: str
    etag: Optional[str] = None
    expires_at: Optional[float] = None
    
    def is_expired(self, max_age: int) -> bool:
        """Check if the cache entry has expired."""
        if self.expires_at and time.time() > self.expires_at:
            return True
        return time.time() - self.created_at > max_age
    
    def touch(self):
        """Update last accessed time and increment access count."""
        self.last_accessed = time.time()
        self.access_count += 1


class StreamingCache:
    """Intelligent caching system for streaming media."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.logger = logging.getLogger('aget.streaming_cache')
        
        # Cache state
        self._cache_index: Dict[str, CacheEntry] = {}
        self._cache_lock = threading.RLock()
        self._total_size = 0
        
        # Background cleanup
        self._cleanup_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
        # Initialize cache
        self._initialize_cache()
        
        if self.config.enable_cache:
            self._start_cleanup_thread()
    
    def _initialize_cache(self):
        """Initialize cache directory and load existing cache index."""
        if not self.config.enable_cache:
            return
        
        # Create cache directory
        cache_path = Path(self.config.cache_dir)
        cache_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing cache index
        index_file = cache_path / "cache_index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
                
                for key, entry_data in index_data.items():
                    entry = CacheEntry(**entry_data)
                    # Verify file still exists
                    if Path(entry.file_path).exists():
                        self._cache_index[key] = entry
                        self._total_size += entry.size
                    
                self.logger.info(f"Loaded {len(self._cache_index)} cache entries, "
                               f"total size: {self._total_size / 1024 / 1024:.2f} MB")
                
            except Exception as e:
                self.logger.warning(f"Failed to load cache index: {e}")
                self._cache_index = {}
                self._total_size = 0
    
    def _save_cache_index(self):
        """Save cache index to disk."""
        if not self.config.enable_cache:
            return
        
        try:
            index_file = Path(self.config.cache_dir) / "cache_index.json"
            index_data = {key: asdict(entry) for key, entry in self._cache_index.items()}
            
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save cache index: {e}")
    
    def _generate_cache_key(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
        """Generate a unique cache key for a URL and headers."""
        # Include relevant headers in cache key
        key_data = url
        if headers:
            # Only include headers that might affect content
            relevant_headers = ['range', 'accept', 'accept-encoding']
            header_parts = []
            for header in relevant_headers:
                if header in headers:
                    header_parts.append(f"{header}:{headers[header]}")
            if header_parts:
                key_data += "|" + "|".join(header_parts)
        
        # Add salt and hash
        key_data += f"|{self.config.cache_key_salt}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str, url: str) -> str:
        """Get the file path for a cache entry."""
        # Extract file extension from URL
        url_path = Path(url.split('?')[0])  # Remove query parameters
        extension = url_path.suffix or '.bin'
        
        # Create subdirectories based on first two characters of hash
        subdir = cache_key[:2]
        cache_dir = Path(self.config.cache_dir) / subdir
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        return str(cache_dir / f"{cache_key}{extension}")
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[Tuple[str, CacheEntry]]:
        """Get cached content for a URL."""
        if not self.config.enable_cache:
            return None
        
        cache_key = self._generate_cache_key(url, headers)
        
        with self._cache_lock:
            entry = self._cache_index.get(cache_key)
            if not entry:
                return None
            
            # Check if entry is expired
            if entry.is_expired(self.config.max_file_age):
                self._remove_entry(cache_key, entry)
                return None
            
            # Check if file still exists
            if not Path(entry.file_path).exists():
                self._remove_entry(cache_key, entry)
                return None
            
            # Update access info
            entry.touch()
            
            self.logger.debug(f"Cache hit for {url}")
            return entry.file_path, entry
    
    def put(self, url: str, content: bytes, content_type: str = "application/octet-stream",
            headers: Optional[Dict[str, str]] = None, etag: Optional[str] = None,
            expires_at: Optional[float] = None) -> str:
        """Store content in cache."""
        if not self.config.enable_cache:
            return ""
        
        cache_key = self._generate_cache_key(url, headers)
        file_path = self._get_cache_file_path(cache_key, url)
        
        try:
            # Write content to file
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Create cache entry
            entry = CacheEntry(
                file_path=file_path,
                url=url,
                size=len(content),
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=1,
                content_type=content_type,
                etag=etag,
                expires_at=expires_at
            )
            
            with self._cache_lock:
                # Remove old entry if exists
                old_entry = self._cache_index.get(cache_key)
                if old_entry:
                    self._total_size -= old_entry.size
                
                # Add new entry
                self._cache_index[cache_key] = entry
                self._total_size += entry.size
                
                # Check cache size limits
                self._enforce_cache_limits()
            
            self.logger.debug(f"Cached {len(content)} bytes for {url}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Failed to cache content for {url}: {e}")
            return ""
    
    def _remove_entry(self, cache_key: str, entry: CacheEntry):
        """Remove a cache entry and its file."""
        try:
            # Remove file
            if Path(entry.file_path).exists():
                os.remove(entry.file_path)
            
            # Remove from index
            if cache_key in self._cache_index:
                del self._cache_index[cache_key]
                self._total_size -= entry.size
                
        except Exception as e:
            self.logger.error(f"Failed to remove cache entry {cache_key}: {e}")
    
    def _enforce_cache_limits(self):
        """Enforce cache size limits using LRU eviction."""
        if self._total_size <= self.config.max_cache_size:
            return
        
        # Sort entries by last accessed time (LRU first)
        entries_by_access = sorted(
            self._cache_index.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove entries until under limit
        target_size = int(self.config.max_cache_size * 0.8)  # Remove to 80% of limit
        
        for cache_key, entry in entries_by_access:
            if self._total_size <= target_size:
                break
            
            self.logger.debug(f"Evicting cache entry: {entry.url}")
            self._remove_entry(cache_key, entry)
        
        self.logger.info(f"Cache cleanup completed. Size: {self._total_size / 1024 / 1024:.2f} MB")
    
    def _cleanup_expired_entries(self):
        """Remove expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        with self._cache_lock:
            for cache_key, entry in self._cache_index.items():
                if entry.is_expired(self.config.max_file_age):
                    expired_keys.append((cache_key, entry))
        
        # Remove expired entries
        for cache_key, entry in expired_keys:
            self.logger.debug(f"Removing expired cache entry: {entry.url}")
            self._remove_entry(cache_key, entry)
        
        if expired_keys:
            self.logger.info(f"Removed {len(expired_keys)} expired cache entries")
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_worker():
            while not self._shutdown_event.wait(self.config.cleanup_interval):
                try:
                    self._cleanup_expired_entries()
                    self._save_cache_index()
                except Exception as e:
                    self.logger.error(f"Error in cache cleanup: {e}")
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        self.logger.info("Started cache cleanup thread")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._cache_lock:
            return {
                'total_entries': len(self._cache_index),
                'total_size_bytes': self._total_size,
                'total_size_mb': self._total_size / 1024 / 1024,
                'cache_hit_ratio': self._calculate_hit_ratio(),
                'oldest_entry': min((e.created_at for e in self._cache_index.values()), default=0),
                'newest_entry': max((e.created_at for e in self._cache_index.values()), default=0),
            }
    
    def _calculate_hit_ratio(self) -> float:
        """Calculate cache hit ratio (placeholder - would need request tracking)."""
        # This would require tracking cache hits/misses over time
        # For now, return a placeholder
        return 0.0
    
    def clear(self):
        """Clear all cache entries."""
        with self._cache_lock:
            for cache_key, entry in list(self._cache_index.items()):
                self._remove_entry(cache_key, entry)
            
            self._cache_index.clear()
            self._total_size = 0
        
        self.logger.info("Cache cleared")
    
    def shutdown(self):
        """Shutdown the cache system."""
        self._shutdown_event.set()
        
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        
        self._save_cache_index()
        self.logger.info("Cache system shutdown")

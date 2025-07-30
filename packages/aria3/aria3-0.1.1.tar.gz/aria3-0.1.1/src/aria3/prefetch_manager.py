"""
Intelligent pre-fetching and bandwidth optimization for streaming proxy.

This module implements smart pre-fetching of upcoming segments based on
playlist analysis and bandwidth monitoring for optimal streaming performance.
"""

import asyncio
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Deque
import logging

from .downloader import MultiThreadDownloader
from .streaming_config import PreFetchConfig, StreamingProxyConfig
from .streaming_cache import StreamingCache
from .playlist_parser import StreamPlaylist, StreamSegment


@dataclass
class BandwidthMeasurement:
    """Represents a bandwidth measurement."""
    timestamp: float
    bytes_downloaded: int
    duration: float
    speed: float  # bytes per second


@dataclass
class PrefetchTask:
    """Represents a pre-fetch task."""
    segment: StreamSegment
    priority: int
    created_at: float
    attempts: int = 0
    max_attempts: int = 3


class BandwidthMonitor:
    """Monitors and tracks bandwidth performance."""
    
    def __init__(self, config: PreFetchConfig):
        self.config = config
        self.logger = logging.getLogger('aget.bandwidth_monitor')
        
        # Bandwidth measurements
        self._measurements: Deque[BandwidthMeasurement] = deque(maxlen=50)
        self._lock = threading.Lock()
        
        # Current bandwidth estimate
        self._current_bandwidth = 0.0
        self._last_update = time.time()
    
    def record_download(self, bytes_downloaded: int, duration: float):
        """Record a download measurement."""
        if duration <= 0:
            return
        
        speed = bytes_downloaded / duration
        measurement = BandwidthMeasurement(
            timestamp=time.time(),
            bytes_downloaded=bytes_downloaded,
            duration=duration,
            speed=speed
        )
        
        with self._lock:
            self._measurements.append(measurement)
            self._update_bandwidth_estimate()
    
    def _update_bandwidth_estimate(self):
        """Update current bandwidth estimate."""
        if not self._measurements:
            return
        
        # Use weighted average of recent measurements
        current_time = time.time()
        total_weight = 0.0
        weighted_speed = 0.0
        
        for measurement in self._measurements:
            # Weight decreases with age (exponential decay)
            age = current_time - measurement.timestamp
            weight = max(0.1, 2.0 ** (-age / 30.0))  # Half-life of 30 seconds
            
            weighted_speed += measurement.speed * weight
            total_weight += weight
        
        if total_weight > 0:
            self._current_bandwidth = weighted_speed / total_weight
            self._last_update = current_time
    
    def get_current_bandwidth(self) -> float:
        """Get current bandwidth estimate in bytes per second."""
        with self._lock:
            # If no recent measurements, return 0
            if time.time() - self._last_update > 60:
                return 0.0
            return self._current_bandwidth
    
    def is_bandwidth_sufficient(self, required_bitrate: float) -> bool:
        """Check if current bandwidth can handle required bitrate."""
        current_bw = self.get_current_bandwidth()
        if current_bw == 0:
            return True  # Assume sufficient if no data
        
        # Add 20% buffer for safety
        return current_bw * 0.8 >= required_bitrate
    
    def get_stats(self) -> Dict:
        """Get bandwidth statistics."""
        with self._lock:
            if not self._measurements:
                return {
                    'current_bandwidth': 0.0,
                    'measurements': 0,
                    'min_speed': 0.0,
                    'max_speed': 0.0,
                    'avg_speed': 0.0
                }
            
            speeds = [m.speed for m in self._measurements]
            return {
                'current_bandwidth': self._current_bandwidth,
                'measurements': len(self._measurements),
                'min_speed': min(speeds),
                'max_speed': max(speeds),
                'avg_speed': sum(speeds) / len(speeds)
            }


class PrefetchManager:
    """Manages intelligent pre-fetching of streaming segments."""
    
    def __init__(self, config: StreamingProxyConfig, cache: StreamingCache):
        self.config = config
        self.cache = cache
        self.logger = logging.getLogger('aget.prefetch_manager')
        
        # Bandwidth monitoring
        self.bandwidth_monitor = BandwidthMonitor(config.prefetch)
        
        # Pre-fetch state
        self._prefetch_queue: Deque[PrefetchTask] = deque()
        self._active_prefetches: Set[str] = set()
        self._completed_segments: Set[str] = set()
        
        # Threading
        self._prefetch_threads: List[threading.Thread] = []
        self._shutdown_event = threading.Event()
        self._queue_lock = threading.Lock()
        
        # Start pre-fetch workers
        if config.prefetch.enable_prefetch:
            self._start_prefetch_workers()
    
    def _start_prefetch_workers(self):
        """Start background pre-fetch worker threads."""
        for i in range(self.config.prefetch.prefetch_threads):
            worker = threading.Thread(
                target=self._prefetch_worker,
                name=f"prefetch-worker-{i}",
                daemon=True
            )
            worker.start()
            self._prefetch_threads.append(worker)
        
        self.logger.info(f"Started {len(self._prefetch_threads)} pre-fetch workers")
    
    def _prefetch_worker(self):
        """Background worker for pre-fetching segments."""
        while not self._shutdown_event.is_set():
            try:
                task = self._get_next_prefetch_task()
                if task:
                    self._execute_prefetch_task(task)
                else:
                    # No tasks, wait a bit
                    time.sleep(1.0)
                    
            except Exception as e:
                self.logger.error(f"Error in pre-fetch worker: {e}")
                time.sleep(5.0)  # Back off on errors
    
    def _get_next_prefetch_task(self) -> Optional[PrefetchTask]:
        """Get the next pre-fetch task from the queue."""
        with self._queue_lock:
            while self._prefetch_queue:
                task = self._prefetch_queue.popleft()
                
                # Skip if already completed or active
                if (task.segment.url in self._completed_segments or
                    task.segment.url in self._active_prefetches):
                    continue
                
                # Check if task is still relevant (not too old)
                if time.time() - task.created_at > 300:  # 5 minutes
                    continue
                
                return task
            
            return None
    
    def _execute_prefetch_task(self, task: PrefetchTask):
        """Execute a pre-fetch task."""
        segment_url = task.segment.url
        
        try:
            # Mark as active
            with self._queue_lock:
                self._active_prefetches.add(segment_url)
            
            # Check if already cached
            if self.cache.get(segment_url):
                self.logger.debug(f"Segment already cached: {segment_url}")
                self._mark_segment_completed(segment_url)
                return
            
            # Check bandwidth before downloading
            if not self._should_prefetch_now():
                # Re-queue with lower priority
                task.priority += 1
                task.attempts += 1
                if task.attempts < task.max_attempts:
                    with self._queue_lock:
                        self._prefetch_queue.append(task)
                self._mark_segment_inactive(segment_url)
                return
            
            # Download segment
            start_time = time.time()
            success = self._download_segment(task.segment)
            download_time = time.time() - start_time
            
            if success:
                # Record bandwidth measurement
                # Note: We'd need to get actual bytes downloaded from the downloader
                # For now, estimate based on typical segment sizes
                estimated_bytes = 1024 * 1024  # 1MB estimate
                self.bandwidth_monitor.record_download(estimated_bytes, download_time)
                
                self._mark_segment_completed(segment_url)
                self.logger.debug(f"Pre-fetched segment: {segment_url}")
            else:
                # Retry with lower priority
                task.attempts += 1
                if task.attempts < task.max_attempts:
                    task.priority += 2
                    with self._queue_lock:
                        self._prefetch_queue.append(task)
                
                self._mark_segment_inactive(segment_url)
                
        except Exception as e:
            self.logger.error(f"Error pre-fetching segment {segment_url}: {e}")
            self._mark_segment_inactive(segment_url)
    
    def _download_segment(self, segment: StreamSegment) -> bool:
        """Download a segment using MultiThreadDownloader."""
        try:
            import tempfile
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Configure downloader for pre-fetching
            download_config = self.config.download
            # Use fewer threads for pre-fetching to not interfere with main downloads
            download_config.max_threads = min(2, download_config.max_threads)
            
            downloader = MultiThreadDownloader(download_config)
            downloader.add_source(segment.url)
            
            # Download
            success = downloader.download(temp_path)
            
            if success:
                # Read and cache content
                with open(temp_path, 'rb') as f:
                    content = f.read()
                
                content_type = self._guess_segment_content_type(segment.url)
                self.cache.put(segment.url, content, content_type)
            
            # Clean up
            import os
            os.unlink(temp_path)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to download segment {segment.url}: {e}")
            return False
    
    def _should_prefetch_now(self) -> bool:
        """Check if we should pre-fetch now based on bandwidth and buffer."""
        # Check bandwidth threshold
        current_bw = self.bandwidth_monitor.get_current_bandwidth()
        if current_bw > 0 and current_bw < self.config.prefetch.min_bandwidth_threshold:
            return False
        
        # Check if too many active pre-fetches
        with self._queue_lock:
            if len(self._active_prefetches) >= self.config.prefetch.prefetch_threads:
                return False
        
        # Additional checks could include:
        # - System resource usage
        # - Time of day policies
        # - User preferences
        
        return True
    
    def _mark_segment_completed(self, segment_url: str):
        """Mark a segment as completed."""
        with self._queue_lock:
            self._completed_segments.add(segment_url)
            self._active_prefetches.discard(segment_url)
    
    def _mark_segment_inactive(self, segment_url: str):
        """Mark a segment as no longer active."""
        with self._queue_lock:
            self._active_prefetches.discard(segment_url)
    
    def _guess_segment_content_type(self, url: str) -> str:
        """Guess content type for a segment."""
        url_lower = url.lower()
        if url_lower.endswith('.ts'):
            return 'video/mp2t'
        elif url_lower.endswith('.m4s'):
            return 'video/iso.segment'
        elif url_lower.endswith('.mp4'):
            return 'video/mp4'
        elif url_lower.endswith('.webm'):
            return 'video/webm'
        else:
            return 'application/octet-stream'
    
    def schedule_prefetch(self, playlist: StreamPlaylist, current_segment_index: int = 0):
        """Schedule pre-fetching for upcoming segments in a playlist."""
        if not self.config.prefetch.enable_prefetch:
            return
        
        # Calculate which segments to pre-fetch
        prefetch_count = self.config.prefetch.prefetch_segments
        start_index = current_segment_index + 1
        end_index = min(start_index + prefetch_count, len(playlist.segments))
        
        tasks_added = 0
        
        for i in range(start_index, end_index):
            segment = playlist.segments[i]
            
            # Skip if already cached or queued
            if (segment.url in self._completed_segments or
                segment.url in self._active_prefetches):
                continue
            
            # Create pre-fetch task
            priority = i - current_segment_index  # Lower number = higher priority
            task = PrefetchTask(
                segment=segment,
                priority=priority,
                created_at=time.time()
            )
            
            with self._queue_lock:
                # Insert in priority order
                inserted = False
                for j, existing_task in enumerate(self._prefetch_queue):
                    if task.priority < existing_task.priority:
                        self._prefetch_queue.insert(j, task)
                        inserted = True
                        break
                
                if not inserted:
                    self._prefetch_queue.append(task)
            
            tasks_added += 1
        
        if tasks_added > 0:
            self.logger.debug(f"Scheduled {tasks_added} segments for pre-fetching")
    
    def get_stats(self) -> Dict:
        """Get pre-fetch statistics."""
        with self._queue_lock:
            return {
                'bandwidth': self.bandwidth_monitor.get_stats(),
                'queue_size': len(self._prefetch_queue),
                'active_prefetches': len(self._active_prefetches),
                'completed_segments': len(self._completed_segments),
                'worker_threads': len(self._prefetch_threads)
            }
    
    def clear_completed_segments(self):
        """Clear the completed segments set to prevent memory growth."""
        with self._queue_lock:
            # Keep only recent segments (last 100)
            if len(self._completed_segments) > 100:
                # Convert to list, sort by some criteria, and keep recent ones
                # For now, just clear old ones
                self._completed_segments.clear()
    
    def shutdown(self):
        """Shutdown the pre-fetch manager."""
        self.logger.info("Shutting down pre-fetch manager")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Wait for workers to finish
        for worker in self._prefetch_threads:
            worker.join(timeout=5.0)
        
        # Clear queues
        with self._queue_lock:
            self._prefetch_queue.clear()
            self._active_prefetches.clear()
        
        self.logger.info("Pre-fetch manager shutdown complete")

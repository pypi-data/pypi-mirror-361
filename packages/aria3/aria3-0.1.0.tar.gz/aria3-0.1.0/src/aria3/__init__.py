"""
aria3 - Advanced multi-threaded download tool (aria2 replacement)

A comprehensive Python library for multi-threaded downloading with advanced features:
- Multi-source downloading with automatic prioritization
- Resumable downloads with range request support
- Dynamic source switching based on performance
- Configurable chunk sizes and thread counts
- Progress tracking and reporting
"""

from .downloader import (
    MultiThreadDownloader,
    DownloadConfig,
    SourceInfo,
    ChunkInfo,
    DownloadProgress,
    download_file
)

# Streaming proxy components
from .streaming_server import StreamingProxyServer
from .streaming_config import (
    StreamingProxyConfig,
    CacheConfig,
    PreFetchConfig,
    StreamingServerConfig,
    AuthConfig,
    load_config
)
from .streaming_cache import StreamingCache
from .playlist_parser import PlaylistParser, StreamPlaylist, StreamSegment
from .prefetch_manager import PrefetchManager, BandwidthMonitor

__version__ = "0.1.0"
__all__ = [
    # Core downloader
    "MultiThreadDownloader",
    "DownloadConfig",
    "SourceInfo",
    "ChunkInfo",
    "DownloadProgress",
    "download_file",

    # Streaming proxy
    "StreamingProxyServer",
    "StreamingProxyConfig",
    "CacheConfig",
    "PreFetchConfig",
    "StreamingServerConfig",
    "AuthConfig",
    "StreamingCache",
    "PlaylistParser",
    "StreamPlaylist",
    "StreamSegment",
    "PrefetchManager",
    "BandwidthMonitor",
    "load_config"
]
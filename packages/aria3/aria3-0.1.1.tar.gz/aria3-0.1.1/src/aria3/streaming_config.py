"""
aget流媒体代理服务器的配置类。

本模块为流媒体代理提供配置选项，包括缓存设置、预取行为、
身份验证和服务器配置。
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, List
from .downloader import DownloadConfig


@dataclass
class CacheConfig:
    """流媒体缓存系统的配置。"""

    # 缓存目录设置
    cache_dir: str = "cache"  # 缓存目录
    max_cache_size: int = 1024 * 1024 * 1024  # 默认1GB
    max_file_age: int = 3600 * 24  # 24小时（秒）
    cleanup_interval: int = 300  # 5分钟（秒）

    # 缓存行为
    enable_cache: bool = True  # 启用缓存
    cache_segments: bool = True  # 缓存片段
    cache_playlists: bool = True  # 缓存播放列表
    cache_key_salt: str = "aget_streaming"  # 缓存键盐值

    def __post_init__(self):
        """确保缓存目录存在。"""
        if self.enable_cache:
            Path(self.cache_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class PreFetchConfig:
    """智能预取的配置。"""

    # 预取行为
    enable_prefetch: bool = True  # 启用预取
    prefetch_segments: int = 3  # 提前预取的片段数量
    prefetch_threads: int = 2  # 专用预取线程数

    # 带宽适应
    enable_bandwidth_adaptation: bool = True  # 启用带宽适应
    bandwidth_check_interval: int = 10  # 带宽检查间隔（秒）
    min_bandwidth_threshold: float = 100 * 1024  # 最小带宽阈值（100 KB/s）

    # 缓冲区管理
    max_buffer_size: int = 50 * 1024 * 1024  # 最大缓冲区大小（50MB）
    buffer_low_watermark: float = 0.3  # 缓冲区低于30%时开始预取
    buffer_high_watermark: float = 0.8  # 缓冲区超过80%时停止预取


@dataclass
class StreamingServerConfig:
    """HTTP流媒体服务器的配置。"""

    # 服务器设置
    host: str = "127.0.0.1"  # 主机地址
    port: int = 8080  # 端口号
    workers: int = 1  # 工作进程数

    # 请求处理
    max_concurrent_streams: int = 10  # 最大并发流数
    request_timeout: int = 30  # 请求超时时间（秒）
    chunk_size: int = 8192  # 流回客户端的块大小

    # CORS和安全
    enable_cors: bool = True  # 启用CORS
    allowed_origins: List[str] = field(default_factory=lambda: ["*"])  # 允许的来源
    max_request_size: int = 1024 * 1024  # 最大请求大小（1MB）

    # 日志记录
    log_level: str = "INFO"  # 日志级别
    access_log: bool = True  # 访问日志
    error_log: bool = True  # 错误日志


@dataclass
class AuthConfig:
    """身份验证和请求头的配置。"""

    # 默认传递的请求头
    default_headers: Dict[str, str] = field(default_factory=dict)  # 默认请求头
    default_cookies: Dict[str, str] = field(default_factory=dict)  # 默认Cookie

    # 身份验证传递
    passthrough_auth_headers: bool = True  # 传递身份验证请求头
    auth_header_whitelist: List[str] = field(default_factory=lambda: [
        "authorization", "cookie", "x-api-key", "x-auth-token"
    ])  # 身份验证请求头白名单

    # 自定义身份验证
    enable_proxy_auth: bool = False  # 启用代理身份验证
    proxy_auth_token: Optional[str] = None  # 代理身份验证令牌
    proxy_auth_header: str = "X-Proxy-Auth"  # 代理身份验证请求头


@dataclass
class StreamingProxyConfig:
    """流媒体代理的主配置类。"""

    # 子配置
    cache: CacheConfig = field(default_factory=CacheConfig)  # 缓存配置
    prefetch: PreFetchConfig = field(default_factory=PreFetchConfig)  # 预取配置
    server: StreamingServerConfig = field(default_factory=StreamingServerConfig)  # 服务器配置
    auth: AuthConfig = field(default_factory=AuthConfig)  # 身份验证配置
    download: DownloadConfig = field(default_factory=DownloadConfig)  # 下载配置

    # 流媒体特定设置
    supported_formats: List[str] = field(default_factory=lambda: [
        "m3u8", "mpd", "ts", "m4s", "mp4", "webm"
    ])  # 支持的格式

    # HLS/DASH特定
    hls_segment_timeout: int = 30  # HLS片段超时时间
    dash_segment_timeout: int = 30  # DASH片段超时时间
    playlist_refresh_interval: int = 5  # 直播流的播放列表刷新间隔（秒）

    # 性能调优
    enable_gzip_compression: bool = True  # 启用gzip压缩
    enable_range_requests: bool = True  # 启用范围请求
    max_redirect_follows: int = 5  # 最大重定向跟随次数
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'StreamingProxyConfig':
        """从字典创建配置。"""
        config = cls()

        # 更新缓存配置
        if 'cache' in config_dict:
            cache_dict = config_dict['cache']
            for key, value in cache_dict.items():
                if hasattr(config.cache, key):
                    setattr(config.cache, key, value)
        
        # Update prefetch config
        if 'prefetch' in config_dict:
            prefetch_dict = config_dict['prefetch']
            for key, value in prefetch_dict.items():
                if hasattr(config.prefetch, key):
                    setattr(config.prefetch, key, value)
        
        # Update server config
        if 'server' in config_dict:
            server_dict = config_dict['server']
            for key, value in server_dict.items():
                if hasattr(config.server, key):
                    setattr(config.server, key, value)
        
        # Update auth config
        if 'auth' in config_dict:
            auth_dict = config_dict['auth']
            for key, value in auth_dict.items():
                if hasattr(config.auth, key):
                    setattr(config.auth, key, value)
        
        # Update download config
        if 'download' in config_dict:
            download_dict = config_dict['download']
            for key, value in download_dict.items():
                if hasattr(config.download, key):
                    setattr(config.download, key, value)
        
        # Update main config
        for key, value in config_dict.items():
            if key not in ['cache', 'prefetch', 'server', 'auth', 'download'] and hasattr(config, key):
                setattr(config, key, value)
        
        return config
    
    @classmethod
    def from_file(cls, config_path: str) -> 'StreamingProxyConfig':
        """Load configuration from JSON or YAML file."""
        import json
        
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                try:
                    import yaml
                    config_dict = yaml.safe_load(f)
                except ImportError:
                    raise ImportError("PyYAML is required to load YAML configuration files")
            else:
                config_dict = json.load(f)
        
        return cls.from_dict(config_dict)
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            'cache': {
                'cache_dir': self.cache.cache_dir,
                'max_cache_size': self.cache.max_cache_size,
                'max_file_age': self.cache.max_file_age,
                'cleanup_interval': self.cache.cleanup_interval,
                'enable_cache': self.cache.enable_cache,
                'cache_segments': self.cache.cache_segments,
                'cache_playlists': self.cache.cache_playlists,
            },
            'prefetch': {
                'enable_prefetch': self.prefetch.enable_prefetch,
                'prefetch_segments': self.prefetch.prefetch_segments,
                'prefetch_threads': self.prefetch.prefetch_threads,
                'enable_bandwidth_adaptation': self.prefetch.enable_bandwidth_adaptation,
                'bandwidth_check_interval': self.prefetch.bandwidth_check_interval,
                'min_bandwidth_threshold': self.prefetch.min_bandwidth_threshold,
                'max_buffer_size': self.prefetch.max_buffer_size,
                'buffer_low_watermark': self.prefetch.buffer_low_watermark,
                'buffer_high_watermark': self.prefetch.buffer_high_watermark,
            },
            'server': {
                'host': self.server.host,
                'port': self.server.port,
                'workers': self.server.workers,
                'max_concurrent_streams': self.server.max_concurrent_streams,
                'request_timeout': self.server.request_timeout,
                'chunk_size': self.server.chunk_size,
                'enable_cors': self.server.enable_cors,
                'allowed_origins': self.server.allowed_origins,
                'max_request_size': self.server.max_request_size,
                'log_level': self.server.log_level,
                'access_log': self.server.access_log,
                'error_log': self.server.error_log,
            },
            'auth': {
                'default_headers': self.auth.default_headers,
                'default_cookies': self.auth.default_cookies,
                'passthrough_auth_headers': self.auth.passthrough_auth_headers,
                'auth_header_whitelist': self.auth.auth_header_whitelist,
                'enable_proxy_auth': self.auth.enable_proxy_auth,
                'proxy_auth_token': self.auth.proxy_auth_token,
                'proxy_auth_header': self.auth.proxy_auth_header,
            },
            'download': {
                'max_chunk_size': self.download.max_chunk_size,
                'max_threads': self.download.max_threads,
                'timeout': self.download.timeout,
                'retry_attempts': self.download.retry_attempts,
                'retry_delay': self.download.retry_delay,
                'speed_threshold': self.download.speed_threshold,
            },
            'supported_formats': self.supported_formats,
            'hls_segment_timeout': self.hls_segment_timeout,
            'dash_segment_timeout': self.dash_segment_timeout,
            'playlist_refresh_interval': self.playlist_refresh_interval,
            'enable_gzip_compression': self.enable_gzip_compression,
            'enable_range_requests': self.enable_range_requests,
            'max_redirect_follows': self.max_redirect_follows,
        }
    
    def save_to_file(self, config_path: str):
        """Save configuration to JSON file."""
        import json
        
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


def get_default_config() -> StreamingProxyConfig:
    """Get default streaming proxy configuration."""
    return StreamingProxyConfig()


def load_config(config_path: Optional[str] = None) -> StreamingProxyConfig:
    """Load configuration from file or return default."""
    if config_path and os.path.exists(config_path):
        return StreamingProxyConfig.from_file(config_path)
    return get_default_config()

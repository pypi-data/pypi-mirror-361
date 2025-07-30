"""
具有高级功能的多线程下载管理器。

本模块提供了一个全面的下载工具，支持：
- 具有可配置块大小的多线程下载
- 具有动态优先级的多源URL
- 自定义请求头和Cookie
- 可恢复下载
- 进度跟踪和报告
- 自动速度监控和源切换
"""

import os
import signal
import sys
import time
import threading
import logging
import hashlib
from typing import List, Dict, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import requests
from tqdm import tqdm


@dataclass
class DownloadConfig:
    """下载操作的配置。"""
    max_chunk_size: int = 1024 * 1024  # 默认1MB
    max_threads: int = 4  # 最大线程数
    timeout: int = 30  # 超时时间（秒）
    retry_attempts: int = 3  # 重试次数
    retry_delay: float = 1.0  # 重试延迟（秒）
    speed_threshold: float = 1024  # 字节每秒 - 低于此值的源被认为是慢速的
    headers: Dict[str, str] = field(default_factory=dict)  # HTTP请求头
    cookies: Dict[str, str] = field(default_factory=dict)  # HTTP Cookie
    user_agent: str = "aget/1.0 (Multi-threaded downloader)"  # 用户代理字符串

    def __post_init__(self):
        """如果未提供则设置默认请求头。"""
        if 'User-Agent' not in self.headers:
            self.headers['User-Agent'] = self.user_agent


@dataclass
class SourceInfo:
    """下载源的信息。"""
    url: str  # 源URL
    priority: float = 1.0  # 优先级
    speed: float = 0.0  # 下载速度（字节/秒）
    last_speed_check: float = 0.0  # 上次速度检查时间
    failures: int = 0  # 失败次数
    active_chunks: int = 0  # 活跃块数量
    total_downloaded: int = 0  # 总下载字节数


@dataclass
class ChunkInfo:
    """下载块的信息。"""
    start: int  # 起始位置
    end: int  # 结束位置
    source_url: str  # 源URL
    downloaded: int = 0  # 已下载字节数
    completed: bool = False  # 是否完成
    thread_id: Optional[int] = None  # 线程ID


class DownloadProgress:
    """线程安全的进度跟踪。"""

    def __init__(self, total_size: int):
        self.total_size = total_size  # 总大小
        self.downloaded = 0  # 已下载大小
        self.start_time = time.time()  # 开始时间
        self.lock = threading.Lock()  # 线程锁
        self.progress_bar = None  # 进度条

    def update(self, bytes_downloaded: int):
        """线程安全地更新进度。"""
        with self.lock:
            self.downloaded += bytes_downloaded
            if self.progress_bar:
                self.progress_bar.update(bytes_downloaded)

    def get_speed(self) -> float:
        """获取当前下载速度（字节/秒）。"""
        with self.lock:
            elapsed = time.time() - self.start_time
            return self.downloaded / elapsed if elapsed > 0 else 0.0

    def get_eta(self) -> float:
        """获取预计完成时间（秒）。"""
        speed = self.get_speed()
        if speed > 0:
            remaining = self.total_size - self.downloaded
            return remaining / speed
        return float('inf')

    def get_progress_percent(self) -> float:
        """获取进度百分比。"""
        return (self.downloaded / self.total_size) * 100 if self.total_size > 0 else 0.0


class MultiThreadDownloader:
    """主要的多线程下载管理器。"""

    def __init__(self, config: Optional[DownloadConfig] = None):
        self.config = config or DownloadConfig()  # 配置
        self.logger = self._setup_logger()  # 日志记录器
        self.sources: List[SourceInfo] = []  # 下载源列表
        self.chunks: List[ChunkInfo] = []  # 下载块列表
        self.progress: Optional[DownloadProgress] = None  # 进度跟踪器
        self.session = requests.Session()  # HTTP会话

        # 中断处理相关
        self._interrupt_count = 0  # 中断计数
        self._download_cancelled = False  # 下载取消标志
        self._original_sigint_handler = None  # 原始信号处理器

        self._setup_session()

    def _setup_logger(self) -> logging.Logger:
        """设置下载器的日志记录。"""
        logger = logging.getLogger('aget.downloader')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def _setup_session(self):
        """配置requests会话。"""
        self.session.headers.update(self.config.headers)
        if self.config.cookies:
            self.session.cookies.update(self.config.cookies)

        # 配置适配器以获得更好的连接池
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=self.config.max_threads,
            pool_maxsize=self.config.max_threads * 2,
            max_retries=0  # 我们手动处理重试
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _setup_signal_handlers(self):
        """设置信号处理器以支持优雅中断。"""
        def signal_handler(signum, frame):
            self._interrupt_count += 1

            if self._interrupt_count == 1:
                print("\n⚠️  检测到中断信号 (Ctrl+C)")
                print("📋 正在尝试优雅停止下载...")
                print("💡 再次按 Ctrl+C 立即强制退出")
                self._download_cancelled = True

                # 给一些时间让下载线程检查取消标志
                threading.Timer(0.5, self._check_graceful_shutdown).start()

            elif self._interrupt_count >= 2:
                print("\n🛑 强制退出下载")
                self._restore_signal_handlers()
                # 强制退出
                os._exit(1)

        # 保存原始处理器并设置新的处理器
        self._original_sigint_handler = signal.signal(signal.SIGINT, signal_handler)

    def _check_graceful_shutdown(self):
        """检查优雅关闭是否完成。"""
        if self._download_cancelled and self._interrupt_count == 1:
            print("⏱️  等待下载线程完成当前块...")
            print("💡 如需立即退出，请再次按 Ctrl+C")

    def _restore_signal_handlers(self):
        """恢复原始信号处理器。"""
        if self._original_sigint_handler is not None:
            signal.signal(signal.SIGINT, self._original_sigint_handler)
            self._original_sigint_handler = None
    
    def add_source(self, url: str, priority: float = 1.0):
        """添加下载源URL。"""
        source = SourceInfo(url=url, priority=priority)
        self.sources.append(source)
        self.logger.info(f"已添加源: {url}，优先级 {priority}")

    def add_sources(self, urls: List[str], priorities: Optional[List[float]] = None):
        """添加多个下载源。"""
        if priorities is None:
            priorities = [1.0] * len(urls)

        for url, priority in zip(urls, priorities):
            self.add_source(url, priority)

    def _get_file_info(self, url: str) -> Tuple[int, bool, Optional[str]]:
        """获取文件大小、范围请求支持和文件名。"""
        file_name = None

        # 首先尝试HEAD请求
        try:
            response = self.session.head(url, timeout=self.config.timeout)
            response.raise_for_status()

            # 获取文件大小
            content_length = response.headers.get('content-length')
            file_size = int(content_length) if content_length else 0

            # 检查服务器是否支持范围请求
            accept_ranges = response.headers.get('accept-ranges', '').lower()
            supports_ranges = accept_ranges == 'bytes'

            # 尝试从Content-Disposition获取文件名
            file_name = self._extract_filename_from_headers(response.headers)

            if file_size > 0:
                self.logger.info(f"文件大小: {file_size} 字节，范围支持: {supports_ranges}")
                if file_name:
                    self.logger.info(f"检测到文件名: {file_name}")
                return file_size, supports_ranges, file_name

        except Exception as e:
            self.logger.warning(f"HEAD请求失败: {e}，尝试使用GET请求获取文件信息")

        # 如果HEAD请求失败或无法获取文件大小，使用GET请求配合Range头
        try:
            # 使用Range请求获取第一个字节来测试范围支持并获取文件大小
            headers = self.config.headers.copy()
            headers['Range'] = 'bytes=0-0'

            response = self.session.get(url, headers=headers, timeout=self.config.timeout)

            # 尝试从响应头获取文件名
            if not file_name:
                file_name = self._extract_filename_from_headers(response.headers)

            # 检查是否返回206 Partial Content
            if response.status_code == 206:
                # 服务器支持范围请求
                content_range = response.headers.get('content-range', '')
                if content_range:
                    # 解析Content-Range头获取文件总大小
                    # 格式: "bytes 0-0/1234" 或 "bytes 0-0/*"
                    try:
                        file_size = int(content_range.split('/')[-1])
                        supports_ranges = True
                        self.logger.info(f"文件大小: {file_size} 字节，范围支持: {supports_ranges}")
                        if file_name:
                            self.logger.info(f"检测到文件名: {file_name}")
                        return file_size, supports_ranges, file_name
                    except (ValueError, IndexError):
                        self.logger.warning(f"无法解析Content-Range头: {content_range}")

            # 如果不支持范围请求或解析失败，尝试从Content-Length获取
            response.raise_for_status()
            content_length = response.headers.get('content-length')
            file_size = int(content_length) if content_length else 0

            # 如果返回200而不是206，说明不支持范围请求
            supports_ranges = response.status_code == 206

            if file_size > 0:
                self.logger.info(f"文件大小: {file_size} 字节，范围支持: {supports_ranges}")
                if file_name:
                    self.logger.info(f"检测到文件名: {file_name}")
                return file_size, supports_ranges, file_name
            else:
                # 如果仍然无法获取文件大小，返回0表示未知大小
                self.logger.warning(f"无法确定文件大小，将使用单线程下载")
                return 0, False, file_name

        except Exception as e:
            self.logger.error(f"从 {url} 获取文件信息失败: {e}")
            raise

    def _extract_filename_from_headers(self, headers: Dict[str, str]) -> Optional[str]:
        """从HTTP响应头中提取文件名。"""
        # 尝试从Content-Disposition头获取文件名
        content_disposition = headers.get('content-disposition', '')
        if content_disposition:
            try:
                # 解析Content-Disposition头
                # 格式可能是: attachment; filename="file.txt" 或 attachment; filename*=UTF-8''file.txt
                if 'filename=' in content_disposition:
                    # 查找filename参数
                    parts = content_disposition.split('filename=')
                    if len(parts) > 1:
                        filename_part = parts[1].strip()

                        # 移除引号
                        if filename_part.startswith('"') and filename_part.endswith('"'):
                            filename_part = filename_part[1:-1]
                        elif filename_part.startswith("'") and filename_part.endswith("'"):
                            filename_part = filename_part[1:-1]

                        # 处理编码问题
                        try:
                            # 尝试ISO-8859-1到UTF-8的转换（常见的HTTP头编码问题）
                            filename = filename_part.encode('iso-8859-1').decode('utf-8')
                        except (UnicodeEncodeError, UnicodeDecodeError):
                            # 如果转换失败，直接使用原始字符串
                            filename = filename_part

                        if filename:
                            return filename

            except Exception as e:
                self.logger.debug(f"解析Content-Disposition头失败: {e}")

        return None

    def _suggest_output_path(self, current_path: str, detected_filename: str) -> str:
        """根据检测到的文件名建议输出路径。"""
        from pathlib import Path

        current_path_obj = Path(current_path)

        # 如果当前路径没有扩展名，或者扩展名是通用的（如.bin），考虑使用检测到的文件名
        current_ext = current_path_obj.suffix.lower()
        detected_ext = Path(detected_filename).suffix.lower()

        # 如果当前路径没有扩展名，或者是通用扩展名，建议使用检测到的文件名
        generic_extensions = {'.bin', '.dat', '.tmp', ''}

        if current_ext in generic_extensions and detected_ext:
            # 保持目录结构，只替换文件名
            suggested_path = current_path_obj.parent / detected_filename
            return str(suggested_path)

        return current_path

    def _create_chunks(self, file_size: int, supports_ranges: bool) -> List[ChunkInfo]:
        """根据文件大小和服务器能力创建下载块。"""
        if not supports_ranges or file_size <= self.config.max_chunk_size:
            # 单块下载
            source_url = self._select_best_source().url
            return [ChunkInfo(start=0, end=file_size-1, source_url=source_url)]

        chunks = []
        chunk_size = min(self.config.max_chunk_size, file_size // self.config.max_threads)

        for i in range(0, file_size, chunk_size):
            start = i
            end = min(i + chunk_size - 1, file_size - 1)
            source_url = self._select_best_source().url
            chunks.append(ChunkInfo(start=start, end=end, source_url=source_url))

        self.logger.info(f"为下载创建了 {len(chunks)} 个块")
        return chunks

    def _select_best_source(self) -> SourceInfo:
        """根据优先级和性能选择最佳源。"""
        if not self.sources:
            raise ValueError("没有可用的源")

        # 按优先级（越高越好）然后按速度排序
        available_sources = [s for s in self.sources if s.failures < self.config.retry_attempts]
        if not available_sources:
            # 如果所有源都失败了，重置失败计数
            for source in self.sources:
                source.failures = 0
            available_sources = self.sources

        # 计算有效优先级（优先级 * 速度因子）
        for source in available_sources:
            if source.speed > 0:
                speed_factor = min(source.speed / self.config.speed_threshold, 2.0)
            else:
                speed_factor = 1.0
            source.effective_priority = source.priority * speed_factor

        return max(available_sources, key=lambda s: s.effective_priority)

    def _download_chunk(self, chunk: ChunkInfo, output_file: str) -> bool:
        """下载单个块。"""
        # 检查是否已取消
        if self._download_cancelled:
            self.logger.info(f"下载已取消，跳过块 {chunk.start}-{chunk.end}")
            return False

        chunk.thread_id = threading.get_ident()
        source = next((s for s in self.sources if s.url == chunk.source_url), None)

        if not source:
            self.logger.error(f"未找到块 {chunk.start}-{chunk.end} 的源")
            return False

        headers = self.config.headers.copy()
        if chunk.start > 0 or chunk.end > 0:
            headers['Range'] = f'bytes={chunk.start}-{chunk.end}'

        start_time = time.time()

        for attempt in range(self.config.retry_attempts):
            try:
                response = self.session.get(
                    chunk.source_url,
                    headers=headers,
                    timeout=self.config.timeout,
                    stream=True
                )
                response.raise_for_status()

                # 更新源活跃块数
                source.active_chunks += 1

                # 写入块数据
                with open(output_file, 'r+b') as f:
                    f.seek(chunk.start + chunk.downloaded)

                    for data in response.iter_content(chunk_size=8192):
                        # 检查是否已取消
                        if self._download_cancelled:
                            self.logger.info(f"下载已取消，停止块 {chunk.start}-{chunk.end}")
                            source.active_chunks -= 1
                            return False

                        if data:
                            f.write(data)
                            chunk.downloaded += len(data)
                            source.total_downloaded += len(data)
                            self.progress.update(len(data))

                # 更新源速度
                elapsed = time.time() - start_time
                if elapsed > 0:
                    source.speed = chunk.downloaded / elapsed
                    source.last_speed_check = time.time()

                chunk.completed = True
                source.active_chunks -= 1

                self.logger.debug(f"从 {chunk.source_url} 完成块 {chunk.start}-{chunk.end}")
                return True

            except Exception as e:
                source.failures += 1
                source.active_chunks = max(0, source.active_chunks - 1)
                self.logger.warning(f"块下载失败（尝试 {attempt + 1}）: {e}")

                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    # 重试时尝试不同的源
                    new_source = self._select_best_source()
                    chunk.source_url = new_source.url
                    source = new_source

        return False

    def _monitor_sources(self):
        """监控源性能并调整优先级。"""
        while not getattr(threading.current_thread(), 'stop_monitoring', False):
            time.sleep(5)  # 每5秒检查一次

            current_time = time.time()
            for source in self.sources:
                # 检查源是否性能不佳
                if (source.speed > 0 and
                    source.speed < self.config.speed_threshold and
                    current_time - source.last_speed_check < 10):

                    # 降低慢速源的优先级
                    source.priority = max(0.1, source.priority * 0.8)
                    self.logger.info(f"降低慢速源 {source.url} 的优先级: {source.priority:.2f}")

                # 如果没有最近的活动，重置速度
                if current_time - source.last_speed_check > 30:
                    source.speed = 0.0

    def download(self, output_path: str, progress_callback: Optional[Callable] = None) -> bool:
        """
        使用多个源和线程下载文件。

        参数:
            output_path: 文件保存路径
            progress_callback: 可选的进度更新回调函数

        返回:
            下载成功返回True，否则返回False
        """
        if not self.sources:
            raise ValueError("未指定下载源")

        # 重置中断状态
        self._interrupt_count = 0
        self._download_cancelled = False

        # 设置信号处理器
        self._setup_signal_handlers()

        try:
            self.logger.info(f"开始下载到 {output_path}")
            return self._do_download(output_path, progress_callback)
        finally:
            # 恢复信号处理器
            self._restore_signal_handlers()

    def _do_download(self, output_path: str, progress_callback: Optional[Callable] = None) -> bool:
        """执行实际的下载过程。"""

        # 从第一个工作的源获取文件信息
        file_size = 0
        supports_ranges = False
        detected_filename = None

        for source in self.sources:
            try:
                file_size, supports_ranges, detected_filename = self._get_file_info(source.url)
                break
            except Exception as e:
                self.logger.warning(f"从 {source.url} 获取信息失败: {e}")
                continue

        if file_size == 0:
            self.logger.error("无法从任何源确定文件大小")
            return False

        # 如果检测到文件名，提供建议
        if detected_filename:
            suggested_path = self._suggest_output_path(output_path, detected_filename)
            if suggested_path != output_path:
                self.logger.info(f"检测到文件名: {detected_filename}")
                self.logger.info(f"建议的输出路径: {suggested_path}")
                # 注意：这里不自动更改路径，只是提供信息

        # 检查文件是否已存在并处理可恢复下载
        resume_position = 0
        if os.path.exists(output_path):
            existing_size = os.path.getsize(output_path)
            if existing_size == file_size:
                self.logger.info("文件已完全下载")
                return True
            elif existing_size < file_size and supports_ranges:
                resume_position = existing_size
                self.logger.info(f"从位置 {resume_position} 恢复下载")
            else:
                self.logger.info("现有文件大小不匹配，开始全新下载")
                os.remove(output_path)

        # Create empty file or truncate existing one
        if resume_position == 0:
            with open(output_path, 'wb') as f:
                f.seek(file_size - 1)
                f.write(b'\0')

        # Create chunks for remaining download
        remaining_size = file_size - resume_position
        self.chunks = self._create_chunks_for_resume(resume_position, file_size, supports_ranges)

        # Initialize progress tracking
        self.progress = DownloadProgress(remaining_size)
        if progress_callback is None:
            self.progress.progress_bar = tqdm(
                total=remaining_size,
                unit='B',
                unit_scale=True,
                desc="Downloading"
            )

        # Start source monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_sources, daemon=True)
        monitor_thread.start()

        # Download chunks using thread pool
        success = True
        with ThreadPoolExecutor(max_workers=self.config.max_threads) as executor:
            future_to_chunk = {
                executor.submit(self._download_chunk, chunk, output_path): chunk
                for chunk in self.chunks
            }

            for future in as_completed(future_to_chunk):
                # 检查是否已取消
                if self._download_cancelled:
                    self.logger.info("下载已取消，停止等待剩余块")
                    # 取消所有未完成的任务
                    for f in future_to_chunk:
                        f.cancel()
                    success = False
                    break

                chunk = future_to_chunk[future]
                try:
                    result = future.result()
                    if not result:
                        self.logger.error(f"Failed to download chunk {chunk.start}-{chunk.end}")
                        success = False
                except Exception as e:
                    self.logger.error(f"Exception in chunk download: {e}")
                    success = False

        # Stop monitoring
        monitor_thread.stop_monitoring = True

        # Close progress bar
        if self.progress.progress_bar:
            self.progress.progress_bar.close()

        if self._download_cancelled:
            print("\n🛑 下载已被用户取消")
            self.logger.info("下载被用户取消")
            return False
        elif success:
            self.logger.info(f"下载成功完成: {output_path}")
            self._log_download_stats()
        else:
            self.logger.error("下载失败")

        return success

    def _create_chunks_for_resume(self, start_pos: int, file_size: int, supports_ranges: bool) -> List[ChunkInfo]:
        """Create chunks for resumable download."""
        if not supports_ranges or (file_size - start_pos) <= self.config.max_chunk_size:
            source_url = self._select_best_source().url
            return [ChunkInfo(start=start_pos, end=file_size-1, source_url=source_url)]

        chunks = []
        remaining_size = file_size - start_pos
        chunk_size = min(self.config.max_chunk_size, remaining_size // self.config.max_threads)

        for i in range(start_pos, file_size, chunk_size):
            start = i
            end = min(i + chunk_size - 1, file_size - 1)
            source_url = self._select_best_source().url
            chunks.append(ChunkInfo(start=start, end=end, source_url=source_url))

        return chunks

    def _log_download_stats(self):
        """记录下载统计信息。"""
        total_time = time.time() - self.progress.start_time
        avg_speed = self.progress.downloaded / total_time if total_time > 0 else 0

        self.logger.info(f"下载统计:")
        self.logger.info(f"  总时间: {total_time:.2f} 秒")
        self.logger.info(f"  平均速度: {avg_speed/1024/1024:.2f} MB/s")
        self.logger.info(f"  总下载量: {self.progress.downloaded/1024/1024:.2f} MB")

        for i, source in enumerate(self.sources):
            self.logger.info(f"  源 {i+1} ({source.url}): {source.total_downloaded/1024/1024:.2f} MB")

    def get_download_info(self) -> Dict[str, Any]:
        """获取当前下载信息。"""
        if not self.progress:
            return {}

        return {
            'total_size': self.progress.total_size,
            'downloaded': self.progress.downloaded,
            'progress_percent': self.progress.get_progress_percent(),
            'speed': self.progress.get_speed(),
            'eta': self.progress.get_eta(),
            'sources': [
                {
                    'url': source.url,
                    'priority': source.priority,
                    'speed': source.speed,
                    'downloaded': source.total_downloaded,
                    'failures': source.failures
                }
                for source in self.sources
            ]
        }


def download_file(urls: List[str], output_path: str, config: Optional[DownloadConfig] = None,
                 priorities: Optional[List[float]] = None) -> bool:
    """
    从多个源下载文件的便利函数。

    参数:
        urls: 源URL列表
        output_path: 文件保存路径
        config: 下载配置（可选）
        priorities: 每个URL的优先级（可选）

    返回:
        下载成功返回True，否则返回False
    """
    downloader = MultiThreadDownloader(config)
    downloader.add_sources(urls, priorities)
    return downloader.download(output_path)

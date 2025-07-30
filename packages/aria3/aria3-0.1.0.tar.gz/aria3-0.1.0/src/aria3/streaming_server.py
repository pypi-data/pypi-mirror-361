"""
FastAPI-based streaming proxy server for aget.

This module implements the HTTP server that handles streaming requests,
proxies content through the multi-threaded downloader, and provides
intelligent caching and pre-fetching.
"""

import asyncio
import io
import logging
import time
from pathlib import Path
from typing import Dict, Optional, Any, List
from urllib.parse import urlparse, parse_qs, unquote

import aiofiles
from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
import uvicorn

from .downloader import MultiThreadDownloader
from .streaming_config import StreamingProxyConfig
from .streaming_cache import StreamingCache
from .playlist_parser import PlaylistParser


class StreamingProxyServer:
    """Main streaming proxy server class."""
    
    def __init__(self, config: StreamingProxyConfig):
        self.config = config
        self.logger = logging.getLogger('aget.streaming_server')
        
        # Initialize components
        self.cache = StreamingCache(config.cache)
        self.playlist_parser = PlaylistParser()
        
        # Active downloads and sessions
        self.active_downloads: Dict[str, MultiThreadDownloader] = {}
        self.session_stats: Dict[str, Dict[str, Any]] = {}
        
        # Create FastAPI app
        self.app = self._create_app()
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
    
    def _create_app(self) -> FastAPI:
        """Create and configure FastAPI application."""
        app = FastAPI(
            title="aget Streaming Proxy",
            description="Multi-threaded streaming proxy with intelligent caching",
            version="1.0.0"
        )
        
        # Add CORS middleware
        if self.config.server.enable_cors:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.server.allowed_origins,
                allow_credentials=True,
                allow_methods=["GET", "HEAD", "OPTIONS"],
                allow_headers=["*"],
            )
        
        # Add routes
        self._add_routes(app)
        
        return app
    
    def _add_routes(self, app: FastAPI):
        """Add routes to the FastAPI application."""
        
        @app.get("/")
        async def root():
            """Root endpoint with server info."""
            return {
                "name": "aget Streaming Proxy",
                "version": "1.0.0",
                "status": "running",
                "cache_stats": self.cache.get_stats()
            }
        
        @app.get("/proxy")
        async def proxy_stream(request: Request, url: str, background_tasks: BackgroundTasks):
            """Main proxy endpoint for streaming content."""
            return await self._handle_proxy_request(request, url, background_tasks)
        
        @app.get("/segment")
        async def proxy_segment(request: Request, url: str, background_tasks: BackgroundTasks):
            """Proxy individual media segments."""
            return await self._handle_segment_request(request, url, background_tasks)
        
        @app.get("/stats")
        async def get_stats():
            """Get server and cache statistics."""
            return {
                "cache": self.cache.get_stats(),
                "active_downloads": len(self.active_downloads),
                "sessions": len(self.session_stats)
            }
        
        @app.post("/cache/clear")
        async def clear_cache():
            """Clear the cache."""
            self.cache.clear()
            return {"status": "cache cleared"}
    
    async def _handle_proxy_request(self, request: Request, url: str, 
                                  background_tasks: BackgroundTasks) -> Response:
        """Handle main proxy requests for playlists and content."""
        try:
            # Decode URL
            original_url = unquote(url)
            self.logger.info(f"Proxy request for: {original_url}")
            
            # Extract headers for passthrough
            headers = self._extract_headers(request)
            
            # Check cache first
            cached_result = self.cache.get(original_url, headers)
            if cached_result:
                file_path, cache_entry = cached_result
                return await self._serve_cached_file(file_path, cache_entry, request)
            
            # Download content
            content, content_type = await self._download_content(original_url, headers)
            if not content:
                raise HTTPException(status_code=404, detail="Content not found")
            
            # Check if this is a playlist
            if self._is_playlist(original_url, content_type):
                # Parse and modify playlist
                modified_content = await self._process_playlist(content, original_url)
                content = modified_content.encode('utf-8')
            
            # Cache the content
            if self.config.cache.enable_cache:
                background_tasks.add_task(
                    self._cache_content_async, original_url, content, content_type, headers
                )
            
            # Return content
            return Response(
                content=content,
                media_type=content_type,
                headers=self._get_response_headers(content_type)
            )
            
        except Exception as e:
            self.logger.error(f"Error handling proxy request: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _handle_segment_request(self, request: Request, url: str,
                                    background_tasks: BackgroundTasks) -> Response:
        """Handle segment requests with streaming support."""
        try:
            original_url = unquote(url)
            self.logger.debug(f"Segment request for: {original_url}")
            
            headers = self._extract_headers(request)
            
            # Check cache first
            cached_result = self.cache.get(original_url, headers)
            if cached_result:
                file_path, cache_entry = cached_result
                return await self._serve_cached_file(file_path, cache_entry, request)
            
            # For segments, we want to stream while downloading
            return await self._stream_download(original_url, headers, request, background_tasks)
            
        except Exception as e:
            self.logger.error(f"Error handling segment request: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _download_content(self, url: str, headers: Dict[str, str]) -> tuple[bytes, str]:
        """Download content using MultiThreadDownloader."""
        try:
            # Create temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
            
            # Configure downloader
            download_config = self.config.download
            download_config.headers.update(headers)
            
            downloader = MultiThreadDownloader(download_config)
            downloader.add_source(url)
            
            # Download
            success = downloader.download(temp_path)
            if not success:
                return b"", ""
            
            # Read content
            with open(temp_path, 'rb') as f:
                content = f.read()
            
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
            
            # Determine content type
            content_type = self._guess_content_type(url, content)
            
            return content, content_type
            
        except Exception as e:
            self.logger.error(f"Failed to download {url}: {e}")
            return b"", ""
    
    async def _stream_download(self, url: str, headers: Dict[str, str], 
                             request: Request, background_tasks: BackgroundTasks) -> StreamingResponse:
        """Stream content while downloading."""
        
        async def generate_stream():
            """Generator for streaming content."""
            try:
                # Create temporary file for download
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # Start download in background
                download_config = self.config.download
                download_config.headers.update(headers)
                
                downloader = MultiThreadDownloader(download_config)
                downloader.add_source(url)
                
                # Start download asynchronously
                import threading
                download_complete = threading.Event()
                download_success = [False]
                
                def download_worker():
                    try:
                        success = downloader.download(temp_path)
                        download_success[0] = success
                    finally:
                        download_complete.set()
                
                download_thread = threading.Thread(target=download_worker)
                download_thread.start()
                
                # Stream content as it becomes available
                file_size = 0
                bytes_sent = 0
                
                while not download_complete.is_set() or bytes_sent < file_size:
                    try:
                        # Check current file size
                        if Path(temp_path).exists():
                            current_size = Path(temp_path).stat().st_size
                            
                            if current_size > bytes_sent:
                                # Read new data
                                with open(temp_path, 'rb') as f:
                                    f.seek(bytes_sent)
                                    chunk = f.read(min(self.config.server.chunk_size, 
                                                     current_size - bytes_sent))
                                    if chunk:
                                        yield chunk
                                        bytes_sent += len(chunk)
                            
                            file_size = current_size
                    
                    except Exception as e:
                        self.logger.error(f"Error streaming {url}: {e}")
                        break
                    
                    # Small delay to avoid busy waiting
                    await asyncio.sleep(0.1)
                
                # Wait for download to complete
                download_thread.join()
                
                # Cache the completed file
                if download_success[0] and Path(temp_path).exists():
                    with open(temp_path, 'rb') as f:
                        content = f.read()
                    
                    content_type = self._guess_content_type(url, content)
                    background_tasks.add_task(
                        self._cache_content_async, url, content, content_type, headers
                    )
                
                # Clean up
                Path(temp_path).unlink(missing_ok=True)
                
            except Exception as e:
                self.logger.error(f"Error in stream generator: {e}")
        
        content_type = self._guess_content_type(url, b"")
        return StreamingResponse(
            generate_stream(),
            media_type=content_type,
            headers=self._get_response_headers(content_type)
        )
    
    async def _serve_cached_file(self, file_path: str, cache_entry, request: Request) -> Response:
        """Serve a cached file with range request support."""
        try:
            file_size = Path(file_path).stat().st_size
            
            # Handle range requests
            range_header = request.headers.get('range')
            if range_header and self.config.enable_range_requests:
                return await self._serve_range_request(file_path, range_header, cache_entry.content_type)
            
            # Serve full file
            return FileResponse(
                file_path,
                media_type=cache_entry.content_type,
                headers=self._get_response_headers(cache_entry.content_type)
            )
            
        except Exception as e:
            self.logger.error(f"Error serving cached file: {e}")
            raise HTTPException(status_code=500, detail="Error serving cached content")
    
    async def _serve_range_request(self, file_path: str, range_header: str, content_type: str) -> Response:
        """Handle HTTP range requests for cached files."""
        try:
            file_size = Path(file_path).stat().st_size
            
            # Parse range header
            range_match = range_header.replace('bytes=', '').split('-')
            start = int(range_match[0]) if range_match[0] else 0
            end = int(range_match[1]) if range_match[1] else file_size - 1
            
            # Validate range
            if start >= file_size or end >= file_size or start > end:
                raise HTTPException(status_code=416, detail="Range not satisfiable")
            
            # Read range
            async with aiofiles.open(file_path, 'rb') as f:
                await f.seek(start)
                content = await f.read(end - start + 1)
            
            headers = {
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(len(content))
            }
            headers.update(self._get_response_headers(content_type))
            
            return Response(
                content=content,
                status_code=206,
                media_type=content_type,
                headers=headers
            )
            
        except Exception as e:
            self.logger.error(f"Error serving range request: {e}")
            raise HTTPException(status_code=500, detail="Error serving range request")
    
    def _extract_headers(self, request: Request) -> Dict[str, str]:
        """Extract relevant headers from request."""
        headers = {}
        
        if self.config.auth.passthrough_auth_headers:
            for header_name in self.config.auth.auth_header_whitelist:
                if header_name in request.headers:
                    headers[header_name] = request.headers[header_name]
        
        # Add default headers
        headers.update(self.config.auth.default_headers)
        
        return headers
    
    def _is_playlist(self, url: str, content_type: str) -> bool:
        """Check if URL/content is a playlist."""
        url_lower = url.lower()
        content_lower = content_type.lower()
        
        return (url_lower.endswith(('.m3u8', '.m3u', '.mpd')) or
                'mpegurl' in content_lower or
                'dash+xml' in content_lower)
    
    async def _process_playlist(self, content: bytes, base_url: str) -> str:
        """Process and modify playlist to use proxy URLs."""
        try:
            content_str = content.decode('utf-8')
            playlist = self.playlist_parser.parse(content_str, base_url)
            
            if not playlist:
                return content_str
            
            # Modify URLs to point to our proxy
            modified_content = content_str
            
            for segment in playlist.segments:
                original_url = segment.url
                proxy_url = f"/segment?url={original_url}"
                modified_content = modified_content.replace(original_url, proxy_url)
            
            return modified_content
            
        except Exception as e:
            self.logger.error(f"Error processing playlist: {e}")
            return content.decode('utf-8', errors='ignore')
    
    def _guess_content_type(self, url: str, content: bytes) -> str:
        """Guess content type from URL and content."""
        url_lower = url.lower()
        
        if url_lower.endswith('.m3u8'):
            return 'application/vnd.apple.mpegurl'
        elif url_lower.endswith('.mpd'):
            return 'application/dash+xml'
        elif url_lower.endswith('.ts'):
            return 'video/mp2t'
        elif url_lower.endswith('.m4s'):
            return 'video/iso.segment'
        elif url_lower.endswith('.mp4'):
            return 'video/mp4'
        elif url_lower.endswith('.webm'):
            return 'video/webm'
        else:
            return 'application/octet-stream'
    
    def _get_response_headers(self, content_type: str) -> Dict[str, str]:
        """Get standard response headers."""
        headers = {
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*',
        }
        
        if self.config.enable_range_requests:
            headers['Accept-Ranges'] = 'bytes'
        
        return headers
    
    async def _cache_content_async(self, url: str, content: bytes, content_type: str, headers: Dict[str, str]):
        """Asynchronously cache content."""
        try:
            self.cache.put(url, content, content_type, headers)
        except Exception as e:
            self.logger.error(f"Error caching content: {e}")
    
    def run(self):
        """Run the streaming server."""
        self.logger.info(f"Starting streaming proxy server on {self.config.server.host}:{self.config.server.port}")
        
        uvicorn.run(
            self.app,
            host=self.config.server.host,
            port=self.config.server.port,
            workers=self.config.server.workers,
            log_level=self.config.server.log_level.lower(),
            access_log=self.config.server.access_log
        )
    
    def shutdown(self):
        """Shutdown the server and cleanup resources."""
        self.logger.info("Shutting down streaming proxy server")
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Shutdown cache
        self.cache.shutdown()
        
        # Clean up active downloads
        for downloader in self.active_downloads.values():
            # Note: MultiThreadDownloader doesn't have explicit cleanup,
            # but we could add it if needed
            pass
        
        self.active_downloads.clear()

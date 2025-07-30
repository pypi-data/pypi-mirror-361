#!/usr/bin/env python3
"""
Command-line interface for the aria3 streaming proxy server.

This module provides a CLI for starting and configuring the streaming proxy
with various options for caching, pre-fetching, and server settings.
"""

import argparse
import json
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

# Handle imports for both direct execution and module import
try:
    from .streaming_server import StreamingProxyServer
    from .streaming_config import StreamingProxyConfig, load_config
    from .prefetch_manager import PrefetchManager
except ImportError:
    # Direct execution
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from aria3.streaming_server import StreamingProxyServer
    from aria3.streaming_config import StreamingProxyConfig, load_config
    from aria3.prefetch_manager import PrefetchManager


class StreamingProxyCLI:
    """Command-line interface for the streaming proxy."""
    
    def __init__(self):
        self.server: Optional[StreamingProxyServer] = None
        self.logger = logging.getLogger('aget.streaming_cli')
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="aget Streaming Proxy - Multi-threaded streaming acceleration",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Start proxy with default settings
  aget-streaming start
  
  # Start with custom port and cache directory
  aget-streaming start --port 9090 --cache-dir /tmp/aget_cache
  
  # Start with configuration file
  aget-streaming start --config config.json
  
  # Generate default configuration
  aget-streaming config --generate config.json
  
  # Show server statistics
  aget-streaming stats --host localhost --port 8080
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Start command
        start_parser = subparsers.add_parser('start', help='Start the streaming proxy server')
        self._add_start_arguments(start_parser)
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Configuration management')
        self._add_config_arguments(config_parser)
        
        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show server statistics')
        self._add_stats_arguments(stats_parser)
        
        # Global options
        parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
        parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode (errors only)')
        
        return parser
    
    def _add_start_arguments(self, parser: argparse.ArgumentParser):
        """Add arguments for the start command."""
        # Configuration
        parser.add_argument('--config', '-c', help='Configuration file path')
        
        # Server settings
        parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
        parser.add_argument('--port', '-p', type=int, default=8080, help='Server port (default: 8080)')
        parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
        
        # Cache settings
        parser.add_argument('--cache-dir', help='Cache directory path')
        parser.add_argument('--cache-size', type=int, help='Maximum cache size in MB')
        parser.add_argument('--no-cache', action='store_true', help='Disable caching')
        
        # Download settings
        parser.add_argument('--threads', '-t', type=int, help='Maximum download threads')
        parser.add_argument('--chunk-size', type=int, help='Download chunk size in KB')
        parser.add_argument('--timeout', type=int, help='Request timeout in seconds')
        
        # Pre-fetch settings
        parser.add_argument('--no-prefetch', action='store_true', help='Disable pre-fetching')
        parser.add_argument('--prefetch-segments', type=int, help='Number of segments to pre-fetch')
        parser.add_argument('--prefetch-threads', type=int, help='Pre-fetch worker threads')
        
        # Authentication
        parser.add_argument('--auth-header', action='append', help='Default auth header (Key: Value)')
        parser.add_argument('--cookie', action='append', help='Default cookie (name=value)')
        
        # Advanced options
        parser.add_argument('--no-cors', action='store_true', help='Disable CORS')
        parser.add_argument('--no-range', action='store_true', help='Disable range requests')
        parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                          default='INFO', help='Log level')
    
    def _add_config_arguments(self, parser: argparse.ArgumentParser):
        """Add arguments for the config command."""
        parser.add_argument('--generate', '-g', help='Generate default configuration file')
        parser.add_argument('--validate', '-v', help='Validate configuration file')
        parser.add_argument('--show', '-s', help='Show configuration from file')
    
    def _add_stats_arguments(self, parser: argparse.ArgumentParser):
        """Add arguments for the stats command."""
        parser.add_argument('--host', default='localhost', help='Server host')
        parser.add_argument('--port', type=int, default=8080, help='Server port')
        parser.add_argument('--format', choices=['json', 'table'], default='table', 
                          help='Output format')
    
    def setup_logging(self, verbose: bool, quiet: bool, log_level: str = 'INFO'):
        """Set up logging configuration."""
        if quiet:
            level = logging.ERROR
        elif verbose:
            level = logging.DEBUG
        else:
            level = getattr(logging, log_level.upper(), logging.INFO)
        
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def create_config_from_args(self, args: argparse.Namespace) -> StreamingProxyConfig:
        """Create configuration from command line arguments."""
        # Load base config
        if args.config:
            config = load_config(args.config)
        else:
            config = StreamingProxyConfig()
        
        # Override with command line arguments
        if hasattr(args, 'host') and args.host:
            config.server.host = args.host
        if hasattr(args, 'port') and args.port:
            config.server.port = args.port
        if hasattr(args, 'workers') and args.workers:
            config.server.workers = args.workers
        
        # Cache settings
        if hasattr(args, 'cache_dir') and args.cache_dir:
            config.cache.cache_dir = args.cache_dir
        if hasattr(args, 'cache_size') and args.cache_size:
            config.cache.max_cache_size = args.cache_size * 1024 * 1024  # Convert MB to bytes
        if hasattr(args, 'no_cache') and args.no_cache:
            config.cache.enable_cache = False
        
        # Download settings
        if hasattr(args, 'threads') and args.threads:
            config.download.max_threads = args.threads
        if hasattr(args, 'chunk_size') and args.chunk_size:
            config.download.max_chunk_size = args.chunk_size * 1024  # Convert KB to bytes
        if hasattr(args, 'timeout') and args.timeout:
            config.download.timeout = args.timeout
        
        # Pre-fetch settings
        if hasattr(args, 'no_prefetch') and args.no_prefetch:
            config.prefetch.enable_prefetch = False
        if hasattr(args, 'prefetch_segments') and args.prefetch_segments:
            config.prefetch.prefetch_segments = args.prefetch_segments
        if hasattr(args, 'prefetch_threads') and args.prefetch_threads:
            config.prefetch.prefetch_threads = args.prefetch_threads
        
        # Authentication
        if hasattr(args, 'auth_header') and args.auth_header:
            for header in args.auth_header:
                if ':' in header:
                    key, value = header.split(':', 1)
                    config.auth.default_headers[key.strip()] = value.strip()
        
        if hasattr(args, 'cookie') and args.cookie:
            for cookie in args.cookie:
                if '=' in cookie:
                    name, value = cookie.split('=', 1)
                    config.auth.default_cookies[name.strip()] = value.strip()
        
        # Advanced options
        if hasattr(args, 'no_cors') and args.no_cors:
            config.server.enable_cors = False
        if hasattr(args, 'no_range') and args.no_range:
            config.enable_range_requests = False
        if hasattr(args, 'log_level') and args.log_level:
            config.server.log_level = args.log_level
        
        return config
    
    def start_command(self, args: argparse.Namespace) -> int:
        """Execute the start command."""
        try:
            # Create configuration
            config = self.create_config_from_args(args)
            
            # Create and start server
            self.server = StreamingProxyServer(config)
            
            # Set up signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                self.logger.info("Received shutdown signal")
                if self.server:
                    self.server.shutdown()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Start server
            self.logger.info("Starting aget streaming proxy server...")
            self.server.run()
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Failed to start server: {e}")
            return 1
    
    def config_command(self, args: argparse.Namespace) -> int:
        """Execute the config command."""
        try:
            if args.generate:
                # Generate default configuration
                config = StreamingProxyConfig()
                config.save_to_file(args.generate)
                print(f"Generated default configuration: {args.generate}")
                return 0
            
            elif args.validate:
                # Validate configuration file
                try:
                    config = load_config(args.validate)
                    print(f"Configuration file is valid: {args.validate}")
                    return 0
                except Exception as e:
                    print(f"Configuration file is invalid: {e}")
                    return 1
            
            elif args.show:
                # Show configuration
                config = load_config(args.show)
                print(json.dumps(config.to_dict(), indent=2))
                return 0
            
            else:
                print("No config action specified. Use --help for options.")
                return 1
                
        except Exception as e:
            self.logger.error(f"Config command failed: {e}")
            return 1
    
    def stats_command(self, args: argparse.Namespace) -> int:
        """Execute the stats command."""
        try:
            import requests
            
            url = f"http://{args.host}:{args.port}/stats"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            stats = response.json()
            
            if args.format == 'json':
                print(json.dumps(stats, indent=2))
            else:
                # Table format
                print("aget Streaming Proxy Statistics")
                print("=" * 40)
                
                # Cache stats
                cache_stats = stats.get('cache', {})
                print(f"Cache Entries: {cache_stats.get('total_entries', 0)}")
                print(f"Cache Size: {cache_stats.get('total_size_mb', 0):.2f} MB")
                
                # Server stats
                print(f"Active Downloads: {stats.get('active_downloads', 0)}")
                print(f"Active Sessions: {stats.get('sessions', 0)}")
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return 1
    
    def run(self, args: list = None) -> int:
        """Run the CLI with given arguments."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        if not parsed_args.command:
            parser.print_help()
            return 1
        
        # Set up logging
        log_level = getattr(parsed_args, 'log_level', 'INFO')
        self.setup_logging(parsed_args.verbose, parsed_args.quiet, log_level)
        
        # Execute command
        if parsed_args.command == 'start':
            return self.start_command(parsed_args)
        elif parsed_args.command == 'config':
            return self.config_command(parsed_args)
        elif parsed_args.command == 'stats':
            return self.stats_command(parsed_args)
        else:
            self.logger.error(f"Unknown command: {parsed_args.command}")
            return 1


def main():
    """Main entry point for the streaming proxy CLI."""
    cli = StreamingProxyCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
aria3多线程下载器的命令行界面。

本模块为使用aria3库及其所有高级功能下载文件提供命令行界面。
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# 如果直接运行，将src目录添加到路径
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from .downloader import MultiThreadDownloader, DownloadConfig
except ImportError:
    from aria3.downloader import MultiThreadDownloader, DownloadConfig


def parse_headers(header_strings: List[str]) -> Dict[str, str]:
    """将格式为'Key: Value'的请求头字符串解析为字典。"""
    headers = {}
    for header_str in header_strings:
        if ':' in header_str:
            key, value = header_str.split(':', 1)
            headers[key.strip()] = value.strip()
        else:
            print(f"警告: 无效的请求头格式 '{header_str}'，期望格式为 'Key: Value'")
    return headers


def parse_cookies(cookie_strings: List[str]) -> Dict[str, str]:
    """将格式为'name=value'的Cookie字符串解析为字典。"""
    cookies = {}
    for cookie_str in cookie_strings:
        if '=' in cookie_str:
            name, value = cookie_str.split('=', 1)
            cookies[name.strip()] = value.strip()
        else:
            print(f"警告: 无效的Cookie格式 '{cookie_str}'，期望格式为 'name=value'")
    return cookies


def setup_logging(verbose: bool, quiet: bool) -> None:
    """根据详细程度标志设置日志记录。"""
    if quiet:
        level = logging.ERROR
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_config(args: argparse.Namespace) -> DownloadConfig:
    """从命令行参数创建DownloadConfig。"""
    headers = parse_headers(args.headers) if args.headers else {}
    cookies = parse_cookies(args.cookies) if args.cookies else {}

    return DownloadConfig(
        max_chunk_size=args.chunk_size,
        max_threads=args.threads,
        timeout=args.timeout,
        retry_attempts=args.retries,
        retry_delay=args.retry_delay,
        speed_threshold=args.speed_threshold,
        headers=headers,
        cookies=cookies,
        user_agent=args.user_agent
    )


def download_command(args: argparse.Namespace) -> int:
    """执行下载命令。"""
    # 如果输出目录不存在则创建
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 创建配置
    config = create_config(args)

    # 创建下载器
    downloader = MultiThreadDownloader(config)

    # 添加带优先级的源
    if args.priorities:
        if len(args.priorities) != len(args.urls):
            print("错误: 优先级数量必须与URL数量匹配")
            return 1
        priorities = args.priorities
    else:
        priorities = [1.0] * len(args.urls)

    downloader.add_sources(args.urls, priorities)

    # 开始下载
    print(f"开始下载到: {args.output}")
    print(f"源数量: {len(args.urls)}")
    print(f"最大线程数: {args.threads}")
    print(f"块大小: {args.chunk_size // 1024}KB")

    success = downloader.download(str(output_path))
    
    if success:
        print(f"\n✓ 下载成功完成: {args.output}")

        if args.stats:
            # 显示详细统计信息
            info = downloader.get_download_info()
            print("\n下载统计:")
            print(f"  总大小: {info['total_size']} 字节")
            print(f"  已下载: {info['downloaded']} 字节")
            print(f"  平均速度: {info['speed']:.2f} 字节/秒")

            print("\n源统计:")
            for i, source in enumerate(info['sources']):
                print(f"  源 {i+1}:")
                print(f"    URL: {source['url']}")
                print(f"    优先级: {source['priority']:.2f}")
                print(f"    速度: {source['speed']:.2f} 字节/秒")
                print(f"    已下载: {source['downloaded']} 字节")
                print(f"    失败次数: {source['failures']}")

        return 0
    else:
        print("\n✗ 下载失败")
        return 1


def info_command(args: argparse.Namespace) -> int:
    """执行info命令获取文件信息。"""
    config = create_config(args)
    downloader = MultiThreadDownloader(config)

    print(f"正在从以下地址获取文件信息: {args.url}")

    try:
        file_size, supports_ranges = downloader._get_file_info(args.url)

        print(f"\n文件信息:")
        print(f"  URL: {args.url}")
        print(f"  大小: {file_size} 字节 ({file_size / 1024 / 1024:.2f} MB)")
        print(f"  支持范围请求: {'是' if supports_ranges else '否'}")

        if supports_ranges:
            estimated_chunks = max(1, file_size // config.max_chunk_size)
            print(f"  预计块数: {estimated_chunks}")

        return 0

    except Exception as e:
        print(f"获取文件信息时出错: {e}")
        return 1


def main():
    """主CLI入口点。"""
    try:
        return _main_impl()
    except KeyboardInterrupt:
        print("\n🛑 程序被用户中断")
        return 130  # 标准的SIGINT退出码

def _main_impl():
    """主CLI实现。"""
    parser = argparse.ArgumentParser(
        description="aget - 高级多线程下载器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 简单下载
  aget download https://example.com/file.zip output.zip

  # 使用自定义设置的多源下载
  aget download -t 8 -c 2048 https://mirror1.com/file.zip https://mirror2.com/file.zip output.zip

  # 使用自定义请求头和Cookie下载
  aget download -H "Authorization: Bearer token" -C "session=abc123" https://api.example.com/file output

  # 获取文件信息
  aget info https://example.com/largefile.zip
        """
    )
    
    # 全局选项
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('-q', '--quiet', action='store_true', help='安静输出（仅错误）')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 下载命令
    download_parser = subparsers.add_parser('download', help='下载文件')
    download_parser.add_argument('urls', nargs='+', help='源URL')
    download_parser.add_argument('output', help='输出文件路径')
    
    # Download options
    download_parser.add_argument('-t', '--threads', type=int, default=4,
                                help='Maximum number of threads (default: 4)')
    download_parser.add_argument('-c', '--chunk-size', type=int, default=1024*1024,
                                help='Maximum chunk size in bytes (default: 1MB)')
    download_parser.add_argument('--timeout', type=int, default=30,
                                help='Request timeout in seconds (default: 30)')
    download_parser.add_argument('--retries', type=int, default=3,
                                help='Number of retry attempts (default: 3)')
    download_parser.add_argument('--retry-delay', type=float, default=1.0,
                                help='Delay between retries in seconds (default: 1.0)')
    download_parser.add_argument('--speed-threshold', type=float, default=1024,
                                help='Speed threshold for slow sources in bytes/s (default: 1024)')
    download_parser.add_argument('-H', '--headers', action='append',
                                help='Custom headers in format "Key: Value"')
    download_parser.add_argument('-C', '--cookies', action='append',
                                help='Custom cookies in format "name=value"')
    download_parser.add_argument('--user-agent', default='aget/1.0',
                                help='User agent string (default: aget/1.0)')
    download_parser.add_argument('-p', '--priorities', type=float, nargs='+',
                                help='Priority for each URL (default: 1.0 for all)')
    download_parser.add_argument('--stats', action='store_true',
                                help='Show detailed download statistics')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Get file information')
    info_parser.add_argument('url', help='File URL')
    info_parser.add_argument('--timeout', type=int, default=30,
                            help='Request timeout in seconds (default: 30)')
    info_parser.add_argument('-H', '--headers', action='append',
                            help='Custom headers in format "Key: Value"')
    info_parser.add_argument('-C', '--cookies', action='append',
                            help='Custom cookies in format "name=value"')
    info_parser.add_argument('--user-agent', default='aget/1.0',
                            help='User agent string (default: aget/1.0)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Set up logging
    setup_logging(args.verbose, args.quiet)
    
    # Execute command
    if args.command == 'download':
        return download_command(args)
    elif args.command == 'info':
        return info_command(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

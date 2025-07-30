"""
Playlist parsing for HLS and DASH streaming formats.

This module provides parsers for HLS (.m3u8) and DASH (.mpd) playlists
to extract segment URLs and metadata for intelligent pre-fetching.
"""

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from urllib.parse import urljoin, urlparse
import logging

try:
    import m3u8
    HAS_M3U8 = True
except ImportError:
    HAS_M3U8 = False


@dataclass
class StreamSegment:
    """Represents a media segment in a stream."""
    
    url: str
    duration: float
    sequence: int
    byte_range: Optional[Tuple[int, int]] = None  # (start, length)
    discontinuity: bool = False
    key_url: Optional[str] = None
    key_iv: Optional[str] = None


@dataclass
class StreamPlaylist:
    """Represents a parsed streaming playlist."""
    
    segments: List[StreamSegment]
    is_live: bool
    target_duration: float
    sequence_start: int
    version: int
    playlist_type: str  # 'hls' or 'dash'
    bandwidth: Optional[int] = None
    resolution: Optional[Tuple[int, int]] = None
    codecs: Optional[str] = None


class HLSParser:
    """Parser for HLS (.m3u8) playlists."""
    
    def __init__(self):
        self.logger = logging.getLogger('aget.hls_parser')
    
    def parse(self, content: str, base_url: str) -> StreamPlaylist:
        """Parse HLS playlist content."""
        if HAS_M3U8:
            return self._parse_with_m3u8(content, base_url)
        else:
            return self._parse_manual(content, base_url)
    
    def _parse_with_m3u8(self, content: str, base_url: str) -> StreamPlaylist:
        """Parse using the m3u8 library."""
        try:
            playlist = m3u8.loads(content, uri=base_url)
            
            segments = []
            for i, segment in enumerate(playlist.segments):
                # Resolve relative URLs
                segment_url = urljoin(base_url, segment.uri)
                
                # Handle byte ranges
                byte_range = None
                if segment.byterange:
                    # Parse byte range format: "length[@offset]"
                    if '@' in segment.byterange:
                        length, offset = segment.byterange.split('@')
                        byte_range = (int(offset), int(length))
                    else:
                        byte_range = (0, int(segment.byterange))
                
                # Handle encryption
                key_url = None
                key_iv = None
                if segment.key and segment.key.uri:
                    key_url = urljoin(base_url, segment.key.uri)
                    key_iv = segment.key.iv
                
                segments.append(StreamSegment(
                    url=segment_url,
                    duration=segment.duration,
                    sequence=playlist.media_sequence + i,
                    byte_range=byte_range,
                    discontinuity=segment.discontinuity,
                    key_url=key_url,
                    key_iv=key_iv
                ))
            
            return StreamPlaylist(
                segments=segments,
                is_live=not playlist.is_endlist,
                target_duration=playlist.target_duration or 10.0,
                sequence_start=playlist.media_sequence or 0,
                version=playlist.version or 1,
                playlist_type='hls'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse HLS playlist with m3u8 library: {e}")
            return self._parse_manual(content, base_url)
    
    def _parse_manual(self, content: str, base_url: str) -> StreamPlaylist:
        """Manual HLS parsing fallback."""
        lines = content.strip().split('\n')
        segments = []
        
        # Parse header info
        target_duration = 10.0
        media_sequence = 0
        version = 1
        is_live = True
        
        i = 0
        segment_duration = 0.0
        segment_sequence = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('#EXT-X-VERSION:'):
                version = int(line.split(':')[1])
            elif line.startswith('#EXT-X-TARGETDURATION:'):
                target_duration = float(line.split(':')[1])
            elif line.startswith('#EXT-X-MEDIA-SEQUENCE:'):
                media_sequence = int(line.split(':')[1])
                segment_sequence = media_sequence
            elif line.startswith('#EXT-X-ENDLIST'):
                is_live = False
            elif line.startswith('#EXTINF:'):
                # Parse segment duration
                duration_match = re.search(r'#EXTINF:([\d.]+)', line)
                if duration_match:
                    segment_duration = float(duration_match.group(1))
            elif line and not line.startswith('#'):
                # This is a segment URL
                segment_url = urljoin(base_url, line)
                segments.append(StreamSegment(
                    url=segment_url,
                    duration=segment_duration,
                    sequence=segment_sequence
                ))
                segment_sequence += 1
                segment_duration = 0.0
            
            i += 1
        
        return StreamPlaylist(
            segments=segments,
            is_live=is_live,
            target_duration=target_duration,
            sequence_start=media_sequence,
            version=version,
            playlist_type='hls'
        )


class DASHParser:
    """Parser for DASH (.mpd) playlists."""
    
    def __init__(self):
        self.logger = logging.getLogger('aget.dash_parser')
    
    def parse(self, content: str, base_url: str) -> StreamPlaylist:
        """Parse DASH MPD content."""
        try:
            root = ET.fromstring(content)
            
            # Extract namespace
            namespace = {'mpd': 'urn:mpeg:dash:schema:mpd:2011'}
            if root.tag.startswith('{'):
                namespace['mpd'] = root.tag.split('}')[0][1:]
            
            # Check if it's a live stream
            is_live = root.get('type', '').lower() == 'dynamic'
            
            # Find adaptation sets and representations
            segments = []
            segment_sequence = 0
            
            for period in root.findall('.//mpd:Period', namespace):
                for adaptation_set in period.findall('.//mpd:AdaptationSet', namespace):
                    for representation in adaptation_set.findall('.//mpd:Representation', namespace):
                        
                        # Get representation info
                        bandwidth = representation.get('bandwidth')
                        width = representation.get('width')
                        height = representation.get('height')
                        
                        # Find segment template or segment list
                        segment_template = representation.find('.//mpd:SegmentTemplate', namespace)
                        segment_list = representation.find('.//mpd:SegmentList', namespace)
                        
                        if segment_template is not None:
                            segments.extend(self._parse_segment_template(
                                segment_template, base_url, segment_sequence, namespace
                            ))
                        elif segment_list is not None:
                            segments.extend(self._parse_segment_list(
                                segment_list, base_url, segment_sequence, namespace
                            ))
                        
                        # For now, just parse the first representation
                        break
                    break
                break
            
            return StreamPlaylist(
                segments=segments,
                is_live=is_live,
                target_duration=10.0,  # Default for DASH
                sequence_start=0,
                version=1,
                playlist_type='dash'
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse DASH MPD: {e}")
            return StreamPlaylist(
                segments=[],
                is_live=False,
                target_duration=10.0,
                sequence_start=0,
                version=1,
                playlist_type='dash'
            )
    
    def _parse_segment_template(self, template_elem, base_url: str, 
                              start_sequence: int, namespace: Dict) -> List[StreamSegment]:
        """Parse DASH SegmentTemplate."""
        segments = []
        
        media_template = template_elem.get('media', '')
        start_number = int(template_elem.get('startNumber', '1'))
        duration = float(template_elem.get('duration', '10'))
        timescale = float(template_elem.get('timescale', '1'))
        
        # Calculate actual duration in seconds
        segment_duration = duration / timescale if timescale > 0 else 10.0
        
        # Find segment timeline or use simple numbering
        timeline = template_elem.find('.//mpd:SegmentTimeline', namespace)
        if timeline is not None:
            # Parse timeline
            for s_elem in timeline.findall('.//mpd:S', namespace):
                repeat = int(s_elem.get('r', '0')) + 1
                for i in range(repeat):
                    segment_number = start_number + len(segments)
                    segment_url = media_template.replace('$Number$', str(segment_number))
                    segment_url = urljoin(base_url, segment_url)
                    
                    segments.append(StreamSegment(
                        url=segment_url,
                        duration=segment_duration,
                        sequence=start_sequence + len(segments)
                    ))
        else:
            # Generate a reasonable number of segments for live content
            num_segments = 10 if template_elem.getparent().getparent().get('type') == 'dynamic' else 1
            for i in range(num_segments):
                segment_number = start_number + i
                segment_url = media_template.replace('$Number$', str(segment_number))
                segment_url = urljoin(base_url, segment_url)
                
                segments.append(StreamSegment(
                    url=segment_url,
                    duration=segment_duration,
                    sequence=start_sequence + i
                ))
        
        return segments
    
    def _parse_segment_list(self, list_elem, base_url: str, 
                           start_sequence: int, namespace: Dict) -> List[StreamSegment]:
        """Parse DASH SegmentList."""
        segments = []
        
        duration = float(list_elem.get('duration', '10'))
        timescale = float(list_elem.get('timescale', '1'))
        segment_duration = duration / timescale if timescale > 0 else 10.0
        
        for i, segment_url_elem in enumerate(list_elem.findall('.//mpd:SegmentURL', namespace)):
            media_url = segment_url_elem.get('media', '')
            segment_url = urljoin(base_url, media_url)
            
            segments.append(StreamSegment(
                url=segment_url,
                duration=segment_duration,
                sequence=start_sequence + i
            ))
        
        return segments


class PlaylistParser:
    """Main playlist parser that handles both HLS and DASH."""
    
    def __init__(self):
        self.hls_parser = HLSParser()
        self.dash_parser = DASHParser()
        self.logger = logging.getLogger('aget.playlist_parser')
    
    def parse(self, content: str, base_url: str, content_type: Optional[str] = None) -> Optional[StreamPlaylist]:
        """Parse playlist content, auto-detecting format."""
        
        # Determine format
        if content_type:
            if 'mpegurl' in content_type or 'm3u8' in content_type:
                format_type = 'hls'
            elif 'dash+xml' in content_type or 'mpd' in content_type:
                format_type = 'dash'
            else:
                format_type = self._detect_format(content, base_url)
        else:
            format_type = self._detect_format(content, base_url)
        
        try:
            if format_type == 'hls':
                return self.hls_parser.parse(content, base_url)
            elif format_type == 'dash':
                return self.dash_parser.parse(content, base_url)
            else:
                self.logger.warning(f"Unknown playlist format for {base_url}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to parse playlist: {e}")
            return None
    
    def _detect_format(self, content: str, base_url: str) -> str:
        """Auto-detect playlist format from content or URL."""
        
        # Check URL extension
        url_lower = base_url.lower()
        if url_lower.endswith('.m3u8') or url_lower.endswith('.m3u'):
            return 'hls'
        elif url_lower.endswith('.mpd'):
            return 'dash'
        
        # Check content
        content_lower = content.lower().strip()
        if content_lower.startswith('#extm3u'):
            return 'hls'
        elif content_lower.startswith('<?xml') and 'mpd' in content_lower:
            return 'dash'
        
        # Default to HLS for unknown formats
        return 'hls'

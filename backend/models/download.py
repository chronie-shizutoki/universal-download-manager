"""
Download task data models
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import re
from urllib.parse import urlparse

class DownloadType(Enum):
    """Download type enumeration"""
    MAGNET = "magnet"
    HTTP = "http"
    HTTPS = "https"
    FTP = "ftp"
    FTPS = "ftps"
    TORRENT = "torrent"

class DownloadStatus(Enum):
    """Download status enumeration"""
    WAITING = "waiting"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETE = "complete"
    ERROR = "error"
    REMOVED = "removed"

@dataclass
class DownloadTask:
    """Download task model"""
    gid: str
    url: str
    download_type: DownloadType
    status: DownloadStatus = DownloadStatus.WAITING
    file_name: str = ""
    file_path: str = ""
    total_length: int = 0
    completed_length: int = 0
    download_speed: int = 0
    upload_speed: int = 0
    progress: float = 0.0
    eta: str = ""
    connections: int = 0
    num_seeders: int = 0
    num_leechers: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: str = ""
    retry_count: int = 0
    priority: int = 0
    category: str = ""
    
    @classmethod
    def from_aria2_response(cls, aria2_data: Dict[str, Any]) -> 'DownloadTask':
        """Create DownloadTask from aria2 RPC response"""
        gid = aria2_data.get('gid', '')
        
        # Determine download type from first URI
        uris = aria2_data.get('files', [{}])[0].get('uris', [])
        url = uris[0].get('uri', '') if uris else ''
        download_type = cls.detect_download_type(url)
        
        # Parse file information
        files = aria2_data.get('files', [])
        file_name = ""
        file_path = ""
        if files:
            file_path = files[0].get('path', '')
            file_name = file_path.split('/')[-1] if file_path else ''
        
        # Parse numeric values
        total_length = int(aria2_data.get('totalLength', 0))
        completed_length = int(aria2_data.get('completedLength', 0))
        download_speed = int(aria2_data.get('downloadSpeed', 0))
        upload_speed = int(aria2_data.get('uploadSpeed', 0))
        
        # Calculate progress
        progress = 0.0
        if total_length > 0:
            progress = (completed_length / total_length) * 100
        
        # Parse status
        status_str = aria2_data.get('status', 'waiting')
        try:
            status = DownloadStatus(status_str)
        except ValueError:
            status = DownloadStatus.WAITING
        
        # Calculate ETA
        eta = cls.calculate_eta(total_length, completed_length, download_speed)
        
        # Determine file category
        category = cls.get_file_category(file_name)
        
        return cls(
            gid=gid,
            url=url,
            download_type=download_type,
            status=status,
            file_name=file_name,
            file_path=file_path,
            total_length=total_length,
            completed_length=completed_length,
            download_speed=download_speed,
            upload_speed=upload_speed,
            progress=round(progress, 1),
            eta=eta,
            connections=int(aria2_data.get('connections', 0)),
            num_seeders=int(aria2_data.get('numSeeders', 0)),
            num_leechers=int(aria2_data.get('numLeechers', 0)),
            category=category
        )
    
    @staticmethod
    def detect_download_type(url: str) -> DownloadType:
        """Detect download type from URL"""
        if not url:
            return DownloadType.HTTP
        
        url_lower = url.lower()
        
        if url_lower.startswith('magnet:'):
            return DownloadType.MAGNET
        elif url_lower.startswith('https:'):
            return DownloadType.HTTPS
        elif url_lower.startswith('http:'):
            return DownloadType.HTTP
        elif url_lower.startswith('ftps:'):
            return DownloadType.FTPS
        elif url_lower.startswith('ftp:'):
            return DownloadType.FTP
        elif url_lower.endswith('.torrent'):
            return DownloadType.TORRENT
        else:
            return DownloadType.HTTP
    
    @staticmethod
    def calculate_eta(total_length: int, completed_length: int, download_speed: int) -> str:
        """Calculate estimated time of arrival"""
        if download_speed <= 0 or total_length <= completed_length:
            return "unknown"
        
        remaining_bytes = total_length - completed_length
        remaining_seconds = remaining_bytes / download_speed
        
        if remaining_seconds < 60:
            return f"{int(remaining_seconds)}s"
        elif remaining_seconds < 3600:
            minutes = int(remaining_seconds / 60)
            return f"{minutes}m"
        else:
            hours = int(remaining_seconds / 3600)
            minutes = int((remaining_seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    @staticmethod
    def get_file_category(file_name: str) -> str:
        """Get file category based on extension"""
        if not file_name:
            return "other"
        
        from ..config.settings import Config
        
        file_ext = '.' + file_name.split('.')[-1].lower() if '.' in file_name else ''
        
        for category, extensions in Config.FILE_CATEGORIES.items():
            if file_ext in extensions:
                return category
        
        return "other"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'gid': self.gid,
            'url': self.url,
            'download_type': self.download_type.value,
            'status': self.status.value,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'total_length': self.total_length,
            'completed_length': self.completed_length,
            'download_speed': self.download_speed,
            'upload_speed': self.upload_speed,
            'progress': self.progress,
            'eta': self.eta,
            'connections': self.connections,
            'num_seeders': self.num_seeders,
            'num_leechers': self.num_leechers,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'priority': self.priority,
            'category': self.category,
            'formatted_total': self.format_size(self.total_length),
            'formatted_completed': self.format_size(self.completed_length),
            'formatted_speed': self.format_speed(self.download_speed),
            'formatted_upload_speed': self.format_speed(self.upload_speed)
        }
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    @staticmethod
    def format_speed(speed_bytes: int) -> str:
        """Format download speed in human readable format"""
        return DownloadTask.format_size(speed_bytes) + "/s"

@dataclass
class UrlInfo:
    """URL information for validation and processing"""
    url: str
    download_type: DownloadType
    is_valid: bool = True
    error_message: str = ""
    file_name: str = ""
    estimated_size: int = 0
    
    @classmethod
    def from_url(cls, url: str) -> 'UrlInfo':
        """Create UrlInfo from URL string"""
        url = url.strip()
        download_type = DownloadTask.detect_download_type(url)
        is_valid, error_message = cls.validate_url(url, download_type)
        
        # Extract filename from URL
        file_name = ""
        if download_type in [DownloadType.HTTP, DownloadType.HTTPS, DownloadType.FTP, DownloadType.FTPS]:
            parsed = urlparse(url)
            file_name = parsed.path.split('/')[-1] if parsed.path else ''
        
        return cls(
            url=url,
            download_type=download_type,
            is_valid=is_valid,
            error_message=error_message,
            file_name=file_name
        )
    
    @staticmethod
    def validate_url(url: str, download_type: DownloadType) -> tuple[bool, str]:
        """Validate URL format"""
        if not url:
            return False, "URL cannot be empty"
        
        if download_type == DownloadType.MAGNET:
            if not url.startswith('magnet:'):
                return False, "Invalid magnet link format"
            if 'xt=' not in url:
                return False, "Magnet link missing hash information"
        
        elif download_type in [DownloadType.HTTP, DownloadType.HTTPS]:
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            if not url_pattern.match(url):
                return False, "Invalid HTTP/HTTPS URL format"
        
        elif download_type in [DownloadType.FTP, DownloadType.FTPS]:
            ftp_pattern = re.compile(
                r'^ftps?://'  # ftp:// or ftps://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/.*)?$', re.IGNORECASE)  # optional path
            
            if not ftp_pattern.match(url):
                return False, "Invalid FTP/FTPS URL format"
        
        return True, ""


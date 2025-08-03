"""
Validation utilities
"""
import re
from urllib.parse import urlparse
from typing import List, Tuple
from ..models.download import DownloadType, UrlInfo

class UrlValidator:
    """URL validation utilities"""
    
    @staticmethod
    def validate_magnet(url: str) -> Tuple[bool, str]:
        """Validate magnet link"""
        if not url.startswith('magnet:'):
            return False, "Invalid magnet link format"
        
        if 'xt=' not in url:
            return False, "Magnet link missing hash information"
        
        # Check for required parameters
        required_params = ['xt']
        for param in required_params:
            if f'{param}=' not in url:
                return False, f"Magnet link missing required parameter: {param}"
        
        return True, ""
    
    @staticmethod
    def validate_http(url: str) -> Tuple[bool, str]:
        """Validate HTTP/HTTPS URL"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False, "Invalid HTTP/HTTPS URL format"
        
        return True, ""
    
    @staticmethod
    def validate_ftp(url: str) -> Tuple[bool, str]:
        """Validate FTP/FTPS URL"""
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
    
    @staticmethod
    def validate_url_list(urls: List[str]) -> List[UrlInfo]:
        """Validate a list of URLs"""
        results = []
        
        for url in urls:
            url = url.strip()
            if not url:
                continue
            
            url_info = UrlInfo.from_url(url)
            results.append(url_info)
        
        return results
    
    @staticmethod
    def parse_url_file(content: str) -> List[str]:
        """Parse URLs from text content"""
        urls = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Extract URL from line (handle various formats)
            url = line.split()[0] if line.split() else line
            
            if url:
                urls.append(url)
        
        return urls

class FileValidator:
    """File validation utilities"""
    
    ALLOWED_EXTENSIONS = {
        'torrent': ['.torrent'],
        'url_list': ['.txt', '.urls', '.list']
    }
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_torrent_file(filename: str, content: bytes) -> Tuple[bool, str]:
        """Validate torrent file"""
        if not filename.lower().endswith('.torrent'):
            return False, "File must have .torrent extension"
        
        if len(content) > FileValidator.MAX_FILE_SIZE:
            return False, "File too large (max 10MB)"
        
        # Basic torrent file validation
        if not content.startswith(b'd'):
            return False, "Invalid torrent file format"
        
        return True, ""
    
    @staticmethod
    def validate_url_list_file(filename: str, content: str) -> Tuple[bool, str]:
        """Validate URL list file"""
        allowed_exts = FileValidator.ALLOWED_EXTENSIONS['url_list']
        
        if not any(filename.lower().endswith(ext) for ext in allowed_exts):
            return False, f"File must have one of these extensions: {', '.join(allowed_exts)}"
        
        if len(content.encode()) > FileValidator.MAX_FILE_SIZE:
            return False, "File too large (max 10MB)"
        
        # Check if file contains valid URLs
        urls = UrlValidator.parse_url_file(content)
        if not urls:
            return False, "File contains no valid URLs"
        
        return True, ""


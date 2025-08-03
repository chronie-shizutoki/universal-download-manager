"""
Download Management Service
"""
import os
import tempfile
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from ..models.download import DownloadTask, DownloadType, UrlInfo
from ..utils.validators import UrlValidator, FileValidator
from ..services.aria2_service import aria2_service
from ..services.i18n_service import i18n
from ..config.settings import Config, DOWNLOADS_DIR

class DownloadService:
    """Service for managing downloads"""
    
    def __init__(self):
        self.aria2 = aria2_service
    
    def add_url(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add single URL download"""
        try:
            # Validate URL
            url_info = UrlInfo.from_url(url)
            if not url_info.is_valid:
                return {
                    'success': False,
                    'error': url_info.error_message,
                    'error_code': 'INVALID_URL'
                }
            
            # Prepare download options
            download_options = self._prepare_download_options(url_info, options)
            
            # Add to aria2
            gid = self.aria2.add_uri([url], download_options)
            
            if gid:
                return {
                    'success': True,
                    'task_id': gid,
                    'url': url,
                    'download_type': url_info.download_type.value
                }
            else:
                return {
                    'success': False,
                    'error': i18n.t('messages.aria2_unavailable'),
                    'error_code': 'ARIA2_ERROR'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def add_magnet(self, magnet_url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add magnet link download"""
        try:
            # Validate magnet link
            is_valid, error_msg = UrlValidator.validate_magnet(magnet_url)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': 'INVALID_MAGNET'
                }
            
            # Prepare download options for BitTorrent
            download_options = self._prepare_bt_options(options)
            
            # Add to aria2
            gid = self.aria2.add_uri([magnet_url], download_options)
            
            if gid:
                return {
                    'success': True,
                    'task_id': gid,
                    'url': magnet_url,
                    'download_type': 'magnet'
                }
            else:
                return {
                    'success': False,
                    'error': i18n.t('messages.aria2_unavailable'),
                    'error_code': 'ARIA2_ERROR'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def add_torrent_file(self, file_content: bytes, filename: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add torrent file download"""
        try:
            # Validate torrent file
            is_valid, error_msg = FileValidator.validate_torrent_file(filename, file_content)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': 'INVALID_TORRENT'
                }
            
            # Prepare download options for BitTorrent
            download_options = self._prepare_bt_options(options)
            
            # Add to aria2
            gid = self.aria2.add_torrent(file_content, download_options)
            
            if gid:
                return {
                    'success': True,
                    'task_id': gid,
                    'filename': filename,
                    'download_type': 'torrent'
                }
            else:
                return {
                    'success': False,
                    'error': i18n.t('messages.aria2_unavailable'),
                    'error_code': 'ARIA2_ERROR'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def add_batch_urls(self, urls: List[str], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add multiple URLs as batch download"""
        try:
            # Validate all URLs
            url_infos = UrlValidator.validate_url_list(urls)
            
            if not url_infos:
                return {
                    'success': False,
                    'error': i18n.t('messages.no_urls_found'),
                    'error_code': 'NO_URLS'
                }
            
            success_count = 0
            fail_count = 0
            results = []
            
            for url_info in url_infos:
                if url_info.is_valid:
                    # Add individual URL
                    result = self.add_url(url_info.url, options)
                    if result['success']:
                        success_count += 1
                        results.append({
                            'url': url_info.url,
                            'success': True,
                            'task_id': result['task_id']
                        })
                    else:
                        fail_count += 1
                        results.append({
                            'url': url_info.url,
                            'success': False,
                            'error': result['error']
                        })
                else:
                    fail_count += 1
                    results.append({
                        'url': url_info.url,
                        'success': False,
                        'error': url_info.error_message
                    })
            
            return {
                'success': success_count > 0,
                'success_count': success_count,
                'fail_count': fail_count,
                'total_count': len(url_infos),
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def add_url_list_file(self, file_content: str, filename: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add URLs from text file"""
        try:
            # Validate URL list file
            is_valid, error_msg = FileValidator.validate_url_list_file(filename, file_content)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'error_code': 'INVALID_FILE'
                }
            
            # Parse URLs from file content
            urls = UrlValidator.parse_url_file(file_content)
            
            if not urls:
                return {
                    'success': False,
                    'error': i18n.t('messages.no_urls_found'),
                    'error_code': 'NO_URLS'
                }
            
            # Add as batch
            return self.add_batch_urls(urls, options)
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def get_downloads(self, status: str = "all", category: str = "", limit: int = 100) -> Dict[str, Any]:
        """Get download list with optional filtering"""
        try:
            downloads = self.aria2.get_downloads(status)
            
            # Filter by category if specified
            if category:
                downloads = [d for d in downloads if d.category == category]
            
            # Limit results
            if limit > 0:
                downloads = downloads[:limit]
            
            return {
                'success': True,
                'downloads': [download.to_dict() for download in downloads],
                'count': len(downloads)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR',
                'downloads': [],
                'count': 0
            }
    
    def get_download(self, gid: str) -> Dict[str, Any]:
        """Get specific download by GID"""
        try:
            download = self.aria2.get_download(gid)
            
            if download:
                return {
                    'success': True,
                    'download': download.to_dict()
                }
            else:
                return {
                    'success': False,
                    'error': 'Download not found',
                    'error_code': 'NOT_FOUND'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def pause_download(self, gid: str) -> Dict[str, Any]:
        """Pause download"""
        try:
            success = self.aria2.pause_download(gid)
            
            if success:
                return {
                    'success': True,
                    'message': i18n.t('messages.download_paused')
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to pause download',
                    'error_code': 'PAUSE_FAILED'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def resume_download(self, gid: str) -> Dict[str, Any]:
        """Resume download"""
        try:
            success = self.aria2.resume_download(gid)
            
            if success:
                return {
                    'success': True,
                    'message': i18n.t('messages.download_resumed')
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to resume download',
                    'error_code': 'RESUME_FAILED'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def remove_download(self, gid: str, force: bool = False) -> Dict[str, Any]:
        """Remove download"""
        try:
            success = self.aria2.remove_download(gid, force)
            
            if success:
                return {
                    'success': True,
                    'message': i18n.t('messages.download_removed')
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to remove download',
                    'error_code': 'REMOVE_FAILED'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def retry_download(self, gid: str) -> Dict[str, Any]:
        """Retry failed download"""
        try:
            # Get download info
            download = self.aria2.get_download(gid)
            if not download:
                return {
                    'success': False,
                    'error': 'Download not found',
                    'error_code': 'NOT_FOUND'
                }
            
            # Remove old download
            self.aria2.remove_download(gid, force=True)
            
            # Re-add download
            if download.download_type == DownloadType.MAGNET:
                result = self.add_magnet(download.url)
            else:
                result = self.add_url(download.url)
            
            if result['success']:
                return {
                    'success': True,
                    'task_id': result['task_id'],
                    'message': i18n.t('messages.download_started')
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get download statistics"""
        try:
            stats = self.aria2.get_stats()
            return {
                'success': True,
                'statistics': stats
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR',
                'statistics': {}
            }
    
    def _prepare_download_options(self, url_info: UrlInfo, custom_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepare download options based on URL type"""
        options = {}
        
        # Set output directory
        options['dir'] = str(DOWNLOADS_DIR)
        
        # Set filename if available
        if url_info.file_name:
            options['out'] = url_info.file_name
        
        # Set user agent
        options['user-agent'] = Config.USER_AGENT
        
        # Set connection limits based on download type
        if url_info.download_type in [DownloadType.HTTP, DownloadType.HTTPS]:
            options['max-connection-per-server'] = str(Config.MAX_CONNECTIONS_PER_SERVER)
            options['split'] = str(Config.MAX_CONNECTIONS_PER_SERVER)
        elif url_info.download_type in [DownloadType.FTP, DownloadType.FTPS]:
            options['max-connection-per-server'] = "1"  # FTP usually doesn't support multiple connections
            options['split'] = "1"
        
        # Set timeout
        options['timeout'] = str(Config.DOWNLOAD_TIMEOUT)
        
        # Set retry options
        options['max-tries'] = str(Config.MAX_RETRIES)
        options['retry-wait'] = str(Config.RETRY_WAIT)
        
        # Apply custom options
        if custom_options:
            options.update(custom_options)
        
        return options
    
    def _prepare_bt_options(self, custom_options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Prepare BitTorrent-specific download options"""
        options = {}
        
        # Set output directory
        options['dir'] = str(DOWNLOADS_DIR)
        
        # BitTorrent specific options
        options['bt-max-peers'] = str(Config.BT_MAX_PEERS)
        options['seed-ratio'] = str(Config.SEED_RATIO)
        options['seed-time'] = str(Config.SEED_TIME)
        
        # Enable DHT and peer exchange
        options['enable-dht'] = 'true'
        options['enable-peer-exchange'] = 'true'
        options['bt-enable-lpd'] = 'true'
        
        # Set listen port
        if Config.BT_LISTEN_PORT:
            options['listen-port'] = str(Config.BT_LISTEN_PORT)
        
        # Apply custom options
        if custom_options:
            options.update(custom_options)
        
        return options

# Global download service instance
download_service = DownloadService()


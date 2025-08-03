"""
File Management Service
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..config.settings import Config, DOWNLOADS_DIR
from ..utils.formatters import SizeFormatter
from ..services.i18n_service import i18n

class FileService:
    """Service for managing downloaded files"""
    
    def __init__(self):
        self.downloads_dir = DOWNLOADS_DIR
        
        # Ensure downloads directory exists
        self.downloads_dir.mkdir(parents=True, exist_ok=True)
    
    def get_files(self, category: str = "", sort_by: str = "name", sort_order: str = "asc") -> Dict[str, Any]:
        """Get list of downloaded files"""
        try:
            files = []
            
            # Scan downloads directory
            for file_path in self._scan_directory(self.downloads_dir):
                if file_path.is_file():
                    file_info = self._get_file_info(file_path)
                    
                    # Filter by category if specified
                    if category and file_info['category'] != category:
                        continue
                    
                    files.append(file_info)
            
            # Sort files
            files = self._sort_files(files, sort_by, sort_order)
            
            return {
                'success': True,
                'files': files,
                'count': len(files),
                'total_size': sum(f['size'] for f in files),
                'formatted_total_size': SizeFormatter.format_bytes(sum(f['size'] for f in files))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR',
                'files': [],
                'count': 0
            }
    
    def get_file_info(self, filename: str) -> Dict[str, Any]:
        """Get information about a specific file"""
        try:
            file_path = self.downloads_dir / filename
            
            if not file_path.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'error_code': 'FILE_NOT_FOUND'
                }
            
            if not file_path.is_file():
                return {
                    'success': False,
                    'error': 'Path is not a file',
                    'error_code': 'NOT_A_FILE'
                }
            
            file_info = self._get_file_info(file_path)
            
            return {
                'success': True,
                'file': file_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def delete_file(self, filename: str) -> Dict[str, Any]:
        """Delete a downloaded file"""
        try:
            file_path = self.downloads_dir / filename
            
            if not file_path.exists():
                return {
                    'success': False,
                    'error': 'File not found',
                    'error_code': 'FILE_NOT_FOUND'
                }
            
            # Check if it's within downloads directory (security check)
            if not self._is_safe_path(file_path):
                return {
                    'success': False,
                    'error': 'Access denied',
                    'error_code': 'ACCESS_DENIED'
                }
            
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path)
            
            return {
                'success': True,
                'message': 'File deleted successfully'
            }
            
        except PermissionError:
            return {
                'success': False,
                'error': 'Permission denied',
                'error_code': 'PERMISSION_DENIED'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def move_file(self, filename: str, destination: str) -> Dict[str, Any]:
        """Move file to different location"""
        try:
            source_path = self.downloads_dir / filename
            dest_path = self.downloads_dir / destination
            
            if not source_path.exists():
                return {
                    'success': False,
                    'error': 'Source file not found',
                    'error_code': 'FILE_NOT_FOUND'
                }
            
            # Security checks
            if not self._is_safe_path(source_path) or not self._is_safe_path(dest_path):
                return {
                    'success': False,
                    'error': 'Access denied',
                    'error_code': 'ACCESS_DENIED'
                }
            
            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(source_path), str(dest_path))
            
            return {
                'success': True,
                'message': 'File moved successfully',
                'new_path': str(dest_path.relative_to(self.downloads_dir))
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def create_directory(self, dirname: str) -> Dict[str, Any]:
        """Create a new directory"""
        try:
            dir_path = self.downloads_dir / dirname
            
            # Security check
            if not self._is_safe_path(dir_path):
                return {
                    'success': False,
                    'error': 'Access denied',
                    'error_code': 'ACCESS_DENIED'
                }
            
            if dir_path.exists():
                return {
                    'success': False,
                    'error': 'Directory already exists',
                    'error_code': 'ALREADY_EXISTS'
                }
            
            dir_path.mkdir(parents=True)
            
            return {
                'success': True,
                'message': 'Directory created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def get_file_path(self, filename: str) -> Optional[Path]:
        """Get full path to a file (for serving downloads)"""
        try:
            file_path = self.downloads_dir / filename
            
            if file_path.exists() and file_path.is_file() and self._is_safe_path(file_path):
                return file_path
            
            return None
            
        except Exception:
            return None
    
    def get_directory_tree(self, path: str = "") -> Dict[str, Any]:
        """Get directory tree structure"""
        try:
            base_path = self.downloads_dir / path if path else self.downloads_dir
            
            if not base_path.exists() or not base_path.is_dir():
                return {
                    'success': False,
                    'error': 'Directory not found',
                    'error_code': 'DIR_NOT_FOUND'
                }
            
            # Security check
            if not self._is_safe_path(base_path):
                return {
                    'success': False,
                    'error': 'Access denied',
                    'error_code': 'ACCESS_DENIED'
                }
            
            tree = self._build_directory_tree(base_path)
            
            return {
                'success': True,
                'tree': tree,
                'path': path
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def cleanup_empty_directories(self) -> Dict[str, Any]:
        """Remove empty directories"""
        try:
            removed_count = 0
            
            for root, dirs, files in os.walk(self.downloads_dir, topdown=False):
                for dirname in dirs:
                    dir_path = Path(root) / dirname
                    try:
                        if not any(dir_path.iterdir()):  # Directory is empty
                            dir_path.rmdir()
                            removed_count += 1
                    except OSError:
                        # Directory not empty or permission error
                        continue
            
            return {
                'success': True,
                'message': f'Removed {removed_count} empty directories',
                'removed_count': removed_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage information"""
        try:
            # Get disk usage for downloads directory
            usage = shutil.disk_usage(self.downloads_dir)
            
            return {
                'success': True,
                'disk_usage': {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'formatted_total': SizeFormatter.format_bytes(usage.total),
                    'formatted_used': SizeFormatter.format_bytes(usage.used),
                    'formatted_free': SizeFormatter.format_bytes(usage.free),
                    'usage_percent': round((usage.used / usage.total) * 100, 1)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }
    
    def _scan_directory(self, directory: Path) -> List[Path]:
        """Recursively scan directory for files"""
        files = []
        
        try:
            for item in directory.rglob('*'):
                if item.is_file():
                    files.append(item)
        except PermissionError:
            # Skip directories we can't access
            pass
        
        return files
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get detailed information about a file"""
        try:
            stat = file_path.stat()
            
            # Get relative path from downloads directory
            relative_path = file_path.relative_to(self.downloads_dir)
            
            # Determine file category
            category = self._get_file_category(file_path.name)
            
            return {
                'name': file_path.name,
                'path': str(relative_path),
                'size': stat.st_size,
                'formatted_size': SizeFormatter.format_bytes(stat.st_size),
                'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'category': category,
                'extension': file_path.suffix.lower(),
                'is_directory': file_path.is_dir()
            }
            
        except Exception as e:
            return {
                'name': file_path.name,
                'path': str(file_path.relative_to(self.downloads_dir)),
                'size': 0,
                'formatted_size': '0 B',
                'created_at': '',
                'modified_at': '',
                'category': 'other',
                'extension': '',
                'is_directory': False,
                'error': str(e)
            }
    
    def _get_file_category(self, filename: str) -> str:
        """Determine file category based on extension"""
        if not filename:
            return "other"
        
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        for category, extensions in Config.FILE_CATEGORIES.items():
            if file_ext in extensions:
                return category
        
        return "other"
    
    def _sort_files(self, files: List[Dict[str, Any]], sort_by: str, sort_order: str) -> List[Dict[str, Any]]:
        """Sort files by specified criteria"""
        reverse = sort_order.lower() == 'desc'
        
        if sort_by == 'name':
            return sorted(files, key=lambda f: f['name'].lower(), reverse=reverse)
        elif sort_by == 'size':
            return sorted(files, key=lambda f: f['size'], reverse=reverse)
        elif sort_by == 'created':
            return sorted(files, key=lambda f: f['created_at'], reverse=reverse)
        elif sort_by == 'modified':
            return sorted(files, key=lambda f: f['modified_at'], reverse=reverse)
        elif sort_by == 'category':
            return sorted(files, key=lambda f: f['category'], reverse=reverse)
        else:
            return files
    
    def _is_safe_path(self, path: Path) -> bool:
        """Check if path is safe (within downloads directory)"""
        try:
            # Resolve path and check if it's within downloads directory
            resolved_path = path.resolve()
            downloads_dir_resolved = self.downloads_dir.resolve()
            
            return str(resolved_path).startswith(str(downloads_dir_resolved))
        except Exception:
            return False
    
    def _build_directory_tree(self, directory: Path, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """Build directory tree structure"""
        if current_depth >= max_depth:
            return {'name': directory.name, 'type': 'directory', 'truncated': True}
        
        tree = {
            'name': directory.name,
            'type': 'directory',
            'children': []
        }
        
        try:
            items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                if item.is_dir():
                    child_tree = self._build_directory_tree(item, max_depth, current_depth + 1)
                    tree['children'].append(child_tree)
                else:
                    file_info = self._get_file_info(item)
                    tree['children'].append({
                        'name': item.name,
                        'type': 'file',
                        'size': file_info['size'],
                        'formatted_size': file_info['formatted_size'],
                        'category': file_info['category']
                    })
        except PermissionError:
            tree['error'] = 'Permission denied'
        
        return tree

# Global file service instance
file_service = FileService()


"""
Formatting utilities
"""
from datetime import datetime, timedelta
from typing import Union

class SizeFormatter:
    """File size formatting utilities"""
    
    @staticmethod
    def format_bytes(size_bytes: int) -> str:
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
        return SizeFormatter.format_bytes(speed_bytes) + "/s"
    
    @staticmethod
    def parse_size(size_str: str) -> int:
        """Parse size string to bytes"""
        size_str = size_str.strip().upper()
        
        if size_str.endswith('B'):
            size_str = size_str[:-1]
        
        multipliers = {
            'K': 1024,
            'M': 1024 ** 2,
            'G': 1024 ** 3,
            'T': 1024 ** 4
        }
        
        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                try:
                    return int(float(size_str[:-1]) * multiplier)
                except ValueError:
                    return 0
        
        try:
            return int(float(size_str))
        except ValueError:
            return 0

class TimeFormatter:
    """Time formatting utilities"""
    
    @staticmethod
    def format_duration(seconds: Union[int, float]) -> str:
        """Format duration in human readable format"""
        if seconds <= 0:
            return "0s"
        
        seconds = int(seconds)
        
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            if remaining_seconds > 0:
                return f"{minutes}m {remaining_seconds}s"
            return f"{minutes}m"
        elif seconds < 86400:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            if remaining_minutes > 0:
                return f"{hours}h {remaining_minutes}m"
            return f"{hours}h"
        else:
            days = seconds // 86400
            remaining_hours = (seconds % 86400) // 3600
            if remaining_hours > 0:
                return f"{days}d {remaining_hours}h"
            return f"{days}d"
    
    @staticmethod
    def format_eta(total_length: int, completed_length: int, download_speed: int) -> str:
        """Calculate and format estimated time of arrival"""
        if download_speed <= 0 or total_length <= completed_length:
            return "unknown"
        
        remaining_bytes = total_length - completed_length
        remaining_seconds = remaining_bytes / download_speed
        
        return TimeFormatter.format_duration(remaining_seconds)
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Format datetime in ISO format"""
        return dt.isoformat() if dt else ""
    
    @staticmethod
    def format_relative_time(dt: datetime) -> str:
        """Format datetime relative to now"""
        if not dt:
            return "unknown"
        
        now = datetime.now()
        diff = now - dt
        
        if diff.total_seconds() < 60:
            return "just now"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = int(diff.total_seconds() / 86400)
            return f"{days} day{'s' if days != 1 else ''} ago"

class ProgressFormatter:
    """Progress formatting utilities"""
    
    @staticmethod
    def format_progress(completed: int, total: int) -> float:
        """Calculate progress percentage"""
        if total <= 0:
            return 0.0
        
        progress = (completed / total) * 100
        return round(progress, 1)
    
    @staticmethod
    def format_progress_bar(progress: float, width: int = 20) -> str:
        """Format progress as ASCII bar"""
        filled = int(progress / 100 * width)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {progress:.1f}%"
    
    @staticmethod
    def format_ratio(uploaded: int, downloaded: int) -> str:
        """Format upload/download ratio"""
        if downloaded <= 0:
            return "∞" if uploaded > 0 else "0.00"
        
        ratio = uploaded / downloaded
        return f"{ratio:.2f}"


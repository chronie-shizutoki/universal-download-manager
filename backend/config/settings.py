"""
Application configuration settings
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
DOWNLOADS_DIR = BASE_DIR / "downloads"
ARIA2_SESSIONS_DIR = BASE_DIR / "aria2_sessions"

# Ensure directories exist
DOWNLOADS_DIR.mkdir(exist_ok=True)
ARIA2_SESSIONS_DIR.mkdir(exist_ok=True)

# Flask configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Download settings
    MAX_CONCURRENT_DOWNLOADS = int(os.environ.get('MAX_CONCURRENT_DOWNLOADS', 5))
    DEFAULT_DOWNLOAD_DIR = str(DOWNLOADS_DIR)
    
    # Supported download types
    SUPPORTED_PROTOCOLS = [
        'magnet',
        'http',
        'https', 
        'ftp',
        'ftps'
    ]
    
    # File type categories
    FILE_CATEGORIES = {
        'video': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
        'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
        'archive': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
        'software': ['.exe', '.msi', '.deb', '.rpm', '.dmg', '.pkg']
    }
    
    # Internationalization
    LANGUAGES = {
        'en': 'English',
        'zh': '中文',
        'ja': '日本語'
    }
    DEFAULT_LANGUAGE = 'en'
    
    # API settings
    API_PREFIX = '/api/v1'
    CORS_ORIGINS = ['*']  # Configure for production
    
    # WebSocket settings
    WEBSOCKET_ENABLED = True
    PROGRESS_UPDATE_INTERVAL = 2  # seconds
    
    # Aria2 settings
    ARIA2_RPC_PORT = int(os.environ.get('ARIA2_RPC_PORT', 6800))
    ARIA2_RPC_SECRET = os.environ.get('ARIA2_RPC_SECRET', None)
    
    # Download settings
    MAX_CONNECTIONS_PER_SERVER = int(os.environ.get('MAX_CONNECTIONS_PER_SERVER', 4))
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', 3))
    RETRY_WAIT = int(os.environ.get('RETRY_WAIT', 5))  # seconds
    DOWNLOAD_TIMEOUT = int(os.environ.get('DOWNLOAD_TIMEOUT', 60))  # seconds
    USER_AGENT = os.environ.get('USER_AGENT', "Universal Download Manager/1.0")
    
    # BitTorrent settings
    BT_MAX_PEERS = int(os.environ.get('BT_MAX_PEERS', 50))
    SEED_RATIO = float(os.environ.get('SEED_RATIO', 1.0))
    SEED_TIME = int(os.environ.get('SEED_TIME', 60))  # minutes
    BT_LISTEN_PORT = int(os.environ.get('BT_LISTEN_PORT', 6881)) if os.environ.get('BT_LISTEN_PORT') else None
    
    # File upload settings
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB


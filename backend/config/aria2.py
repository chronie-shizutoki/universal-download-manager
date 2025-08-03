"""
Aria2c configuration settings
"""
import os
from .settings import DOWNLOADS_DIR, ARIA2_SESSIONS_DIR

class Aria2Config:
    """Aria2c daemon configuration"""
    
    # RPC settings
    RPC_HOST = os.environ.get('ARIA2_RPC_HOST', 'localhost')
    RPC_PORT = int(os.environ.get('ARIA2_RPC_PORT', 6800))
    RPC_SECRET = os.environ.get('ARIA2_RPC_SECRET', 'mysecret')
    RPC_URL = f"http://{RPC_HOST}:{RPC_PORT}/jsonrpc"
    
    # Download settings
    DOWNLOAD_DIR = str(DOWNLOADS_DIR)
    MAX_CONCURRENT_DOWNLOADS = int(os.environ.get('ARIA2_MAX_CONCURRENT', 5))
    MAX_CONNECTION_PER_SERVER = int(os.environ.get('ARIA2_MAX_CONN_PER_SERVER', 10))
    MIN_SPLIT_SIZE = os.environ.get('ARIA2_MIN_SPLIT_SIZE', '5M')
    SPLIT = int(os.environ.get('ARIA2_SPLIT', 16))
    
    # Speed limits
    MAX_OVERALL_DOWNLOAD_LIMIT = os.environ.get('ARIA2_MAX_OVERALL_SPEED', '0')  # 0 = unlimited
    MAX_DOWNLOAD_LIMIT = os.environ.get('ARIA2_MAX_SPEED_PER_DOWNLOAD', '0')
    MAX_UPLOAD_LIMIT = os.environ.get('ARIA2_MAX_UPLOAD_SPEED', '5M')
    
    # BitTorrent settings
    BT_TRACKER_LIST = [
        "http://tracker.opentrackr.org:1337/announce",
        "udp://tracker.opentrackr.org:1337/announce",
        "udp://open.stealth.si:80/announce",
        "udp://tracker.openbittorrent.com:80/announce",
        "udp://exodus.desync.com:6969/announce",
        "udp://tracker.torrent.eu.org:451/announce",
        "udp://tracker.moeking.me:6969/announce",
        "udp://ipv4.tracker.harry.lu:80/announce",
        "udp://open.demonii.si:1337/announce",
        "udp://tracker.pomf.se:80/announce",
        "udp://tracker.tiny-vps.com:6969/announce",
        "udp://bt1.archive.org:6969/announce",
        "udp://bt2.archive.org:6969/announce",
        "udp://tracker.dler.org:6969/announce"
    ]
    
    SEED_TIME = int(os.environ.get('ARIA2_SEED_TIME', 0))  # 0 = no seeding
    BT_MAX_PEERS = int(os.environ.get('ARIA2_BT_MAX_PEERS', 100))
    
    # Network settings
    LISTEN_PORT = os.environ.get('ARIA2_LISTEN_PORT', '6881-6999')
    DHT_LISTEN_PORT = os.environ.get('ARIA2_DHT_LISTEN_PORT', '6881-6999')
    
    # Retry settings
    TIMEOUT = int(os.environ.get('ARIA2_TIMEOUT', 60))
    RETRY_WAIT = int(os.environ.get('ARIA2_RETRY_WAIT', 30))
    MAX_TRIES = int(os.environ.get('ARIA2_MAX_TRIES', 5))
    
    # Session settings
    SESSION_FILE = str(ARIA2_SESSIONS_DIR / "aria2.session")
    
    @classmethod
    def get_daemon_args(cls):
        """Get aria2c daemon command line arguments"""
        args = [
            "--enable-rpc",
            "--rpc-listen-all",
            f"--rpc-listen-port={cls.RPC_PORT}",
            f"--rpc-secret={cls.RPC_SECRET}",
            f"--dir={cls.DOWNLOAD_DIR}",
            f"--max-concurrent-downloads={cls.MAX_CONCURRENT_DOWNLOADS}",
            f"--max-connection-per-server={cls.MAX_CONNECTION_PER_SERVER}",
            f"--min-split-size={cls.MIN_SPLIT_SIZE}",
            f"--split={cls.SPLIT}",
            f"--seed-time={cls.SEED_TIME}",
            f"--max-upload-limit={cls.MAX_UPLOAD_LIMIT}",
            f"--bt-max-peers={cls.BT_MAX_PEERS}",
            f"--listen-port={cls.LISTEN_PORT}",
            f"--dht-listen-port={cls.DHT_LISTEN_PORT}",
            f"--timeout={cls.TIMEOUT}",
            f"--retry-wait={cls.RETRY_WAIT}",
            f"--max-tries={cls.MAX_TRIES}",
            f"--input-file={cls.SESSION_FILE}",
            f"--save-session={cls.SESSION_FILE}",
            "--enable-dht=true",
            "--enable-dht6=true", 
            "--enable-peer-exchange=true",
            "--bt-enable-lpd=true",
            "--continue=true",
            "--allow-overwrite=true",
            "--auto-file-renaming=false",
            "--summary-interval=1",
            "--log-level=info",
            "--console-log-level=info"
        ]
        
        # Add tracker list
        if cls.BT_TRACKER_LIST:
            tracker_str = ",".join(cls.BT_TRACKER_LIST)
            args.append(f"--bt-tracker={tracker_str}")
        
        # Add speed limits if set
        if cls.MAX_OVERALL_DOWNLOAD_LIMIT != '0':
            args.append(f"--max-overall-download-limit={cls.MAX_OVERALL_DOWNLOAD_LIMIT}")
        
        if cls.MAX_DOWNLOAD_LIMIT != '0':
            args.append(f"--max-download-limit={cls.MAX_DOWNLOAD_LIMIT}")
        
        return args
    
    @classmethod
    def get_rpc_params(cls, method, params=None):
        """Get RPC request parameters"""
        if params is None:
            params = []
        
        # Add secret token as first parameter
        params.insert(0, f"token:{cls.RPC_SECRET}")
        
        return {
            "jsonrpc": "2.0",
            "id": "1", 
            "method": method,
            "params": params
        }


"""
Aria2 RPC Service
"""
import json
import requests
import subprocess
import time
import os
import signal
from typing import Dict, List, Optional, Any, Tuple
from ..config.settings import Config, DOWNLOADS_DIR
from ..config.aria2 import Aria2Config
from ..models.download import DownloadTask, DownloadType, DownloadStatus
from ..utils.formatters import SizeFormatter, TimeFormatter

class Aria2Service:
    """Service for managing aria2c daemon and RPC communications"""
    
    def __init__(self):
        self.rpc_url = f"http://localhost:{Config.ARIA2_RPC_PORT}/jsonrpc"
        self.rpc_secret = Config.ARIA2_RPC_SECRET
        self.process = None
        self.session_file = DOWNLOADS_DIR / "aria2.session"
        
    def start_daemon(self) -> bool:
        """Start aria2c daemon if not running"""
        if self.is_daemon_running():
            return True
        
        try:
            # Ensure downloads directory exists
            DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
            
            # Create session file if it doesn't exist
            if not self.session_file.exists():
                self.session_file.touch()
            
            # Build aria2c command
            cmd = self._build_aria2_command()
            
            # Start daemon
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid  # Create new process group
            )
            
            # Wait for daemon to start
            for _ in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                if self.is_daemon_running():
                    return True
            
            return False
            
        except Exception as e:
            print(f"Failed to start aria2c daemon: {e}")
            return False
    
    def stop_daemon(self) -> bool:
        """Stop aria2c daemon"""
        try:
            # Try graceful shutdown via RPC
            if self.is_daemon_running():
                try:
                    self.rpc_call("aria2.shutdown")
                    time.sleep(2)
                except:
                    pass
            
            # Force kill if still running
            if self.process and self.process.poll() is None:
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                time.sleep(2)
                
                if self.process.poll() is None:
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            
            return True
            
        except Exception as e:
            print(f"Failed to stop aria2c daemon: {e}")
            return False
    
    def is_daemon_running(self) -> bool:
        """Check if aria2c daemon is running"""
        try:
            response = self.rpc_call("aria2.getVersion")
            return response is not None
        except:
            return False
    
    def is_aria2_available(self) -> Tuple[bool, str]:
        """Check if aria2c is available on system"""
        try:
            result = subprocess.run(
                ["aria2c", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                version = version_line.split()[1] if len(version_line.split()) > 1 else "unknown"
                return True, version
            else:
                return False, "aria2c command failed"
                
        except subprocess.TimeoutExpired:
            return False, "aria2c command timeout"
        except FileNotFoundError:
            return False, "aria2c not found in PATH"
        except Exception as e:
            return False, str(e)
    
    def _build_aria2_command(self) -> List[str]:
        """Build aria2c command with configuration"""
        cmd = [
            "aria2c",
            "--enable-rpc",
            f"--rpc-listen-port={Config.ARIA2_RPC_PORT}",
            "--rpc-allow-origin-all",
            f"--dir={DOWNLOADS_DIR}",
            f"--input-file={self.session_file}",
            f"--save-session={self.session_file}",
            "--save-session-interval=60",
            "--daemon"
        ]
        
        # Add RPC secret if configured
        if self.rpc_secret:
            cmd.append(f"--rpc-secret={self.rpc_secret}")
        
        # Add aria2 configuration options
        aria2_config = Aria2Config.get_config()
        for key, value in aria2_config.items():
            if value is not None:
                cmd.append(f"--{key}={value}")
        
        return cmd
    
    def rpc_call(self, method: str, params: List[Any] = None) -> Optional[Dict[str, Any]]:
        """Make RPC call to aria2c daemon"""
        if params is None:
            params = []
        
        # Add secret token if configured
        if self.rpc_secret:
            params.insert(0, f"token:{self.rpc_secret}")
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": "1"
        }
        
        try:
            response = requests.post(
                self.rpc_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                print(f"RPC error: {result['error']}")
                return None
            
            return result.get("result")
            
        except requests.exceptions.RequestException as e:
            print(f"RPC request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"RPC response decode failed: {e}")
            return None
        except Exception as e:
            print(f"RPC call failed: {e}")
            return None
    
    def add_uri(self, uris: List[str], options: Dict[str, Any] = None) -> Optional[str]:
        """Add download by URI(s)"""
        if options is None:
            options = {}
        
        result = self.rpc_call("aria2.addUri", [uris, options])
        return result if result else None
    
    def add_torrent(self, torrent_data: bytes, options: Dict[str, Any] = None) -> Optional[str]:
        """Add download by torrent data"""
        if options is None:
            options = {}
        
        import base64
        torrent_b64 = base64.b64encode(torrent_data).decode('utf-8')
        
        result = self.rpc_call("aria2.addTorrent", [torrent_b64, [], options])
        return result if result else None
    
    def add_metalink(self, metalink_data: bytes, options: Dict[str, Any] = None) -> Optional[str]:
        """Add download by metalink data"""
        if options is None:
            options = {}
        
        import base64
        metalink_b64 = base64.b64encode(metalink_data).decode('utf-8')
        
        result = self.rpc_call("aria2.addMetalink", [metalink_b64, options])
        return result if result else None
    
    def get_downloads(self, status: str = "all") -> List[DownloadTask]:
        """Get download tasks by status"""
        downloads = []
        
        try:
            if status == "all":
                # Get active, waiting, and stopped downloads
                active = self.rpc_call("aria2.tellActive") or []
                waiting = self.rpc_call("aria2.tellWaiting", [0, 100]) or []
                stopped = self.rpc_call("aria2.tellStopped", [0, 100]) or []
                
                all_downloads = active + waiting + stopped
            elif status == "active":
                all_downloads = self.rpc_call("aria2.tellActive") or []
            elif status == "waiting":
                all_downloads = self.rpc_call("aria2.tellWaiting", [0, 100]) or []
            elif status == "stopped":
                all_downloads = self.rpc_call("aria2.tellStopped", [0, 100]) or []
            else:
                all_downloads = []
            
            for download_data in all_downloads:
                try:
                    download = DownloadTask.from_aria2_response(download_data)
                    downloads.append(download)
                except Exception as e:
                    print(f"Failed to parse download data: {e}")
                    continue
            
        except Exception as e:
            print(f"Failed to get downloads: {e}")
        
        return downloads
    
    def get_download(self, gid: str) -> Optional[DownloadTask]:
        """Get specific download by GID"""
        try:
            download_data = self.rpc_call("aria2.tellStatus", [gid])
            if download_data:
                return DownloadTask.from_aria2_response(download_data)
        except Exception as e:
            print(f"Failed to get download {gid}: {e}")
        
        return None
    
    def pause_download(self, gid: str) -> bool:
        """Pause download"""
        try:
            result = self.rpc_call("aria2.pause", [gid])
            return result == gid
        except Exception as e:
            print(f"Failed to pause download {gid}: {e}")
            return False
    
    def resume_download(self, gid: str) -> bool:
        """Resume download"""
        try:
            result = self.rpc_call("aria2.unpause", [gid])
            return result == gid
        except Exception as e:
            print(f"Failed to resume download {gid}: {e}")
            return False
    
    def remove_download(self, gid: str, force: bool = False) -> bool:
        """Remove download"""
        try:
            method = "aria2.forceRemove" if force else "aria2.remove"
            result = self.rpc_call(method, [gid])
            return result == gid
        except Exception as e:
            print(f"Failed to remove download {gid}: {e}")
            return False
    
    def pause_all(self) -> bool:
        """Pause all downloads"""
        try:
            result = self.rpc_call("aria2.pauseAll")
            return result == "OK"
        except Exception as e:
            print(f"Failed to pause all downloads: {e}")
            return False
    
    def resume_all(self) -> bool:
        """Resume all downloads"""
        try:
            result = self.rpc_call("aria2.unpauseAll")
            return result == "OK"
        except Exception as e:
            print(f"Failed to resume all downloads: {e}")
            return False
    
    def purge_completed(self) -> bool:
        """Purge completed/error/removed downloads"""
        try:
            result = self.rpc_call("aria2.purgeDownloadResult")
            return result == "OK"
        except Exception as e:
            print(f"Failed to purge completed downloads: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get global statistics"""
        try:
            stats = self.rpc_call("aria2.getGlobalStat")
            if stats:
                return {
                    'download_speed': int(stats.get('downloadSpeed', 0)),
                    'upload_speed': int(stats.get('uploadSpeed', 0)),
                    'active_downloads': int(stats.get('numActive', 0)),
                    'waiting_downloads': int(stats.get('numWaiting', 0)),
                    'stopped_downloads': int(stats.get('numStopped', 0)),
                    'formatted_download_speed': SizeFormatter.format_speed(int(stats.get('downloadSpeed', 0))),
                    'formatted_upload_speed': SizeFormatter.format_speed(int(stats.get('uploadSpeed', 0)))
                }
        except Exception as e:
            print(f"Failed to get stats: {e}")
        
        return {
            'download_speed': 0,
            'upload_speed': 0,
            'active_downloads': 0,
            'waiting_downloads': 0,
            'stopped_downloads': 0,
            'formatted_download_speed': '0 B/s',
            'formatted_upload_speed': '0 B/s'
        }
    
    def get_version(self) -> Optional[Dict[str, Any]]:
        """Get aria2 version information"""
        try:
            return self.rpc_call("aria2.getVersion")
        except Exception as e:
            print(f"Failed to get version: {e}")
            return None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test aria2 availability and RPC connection"""
        # Check if aria2c is available
        aria2_available, version_or_error = self.is_aria2_available()
        
        result = {
            'aria2c_available': aria2_available,
            'version': version_or_error if aria2_available else None,
            'error': version_or_error if not aria2_available else None,
            'daemon_running': False,
            'rpc_status': False
        }
        
        if not aria2_available:
            return result
        
        # Check if daemon is running
        daemon_running = self.is_daemon_running()
        result['daemon_running'] = daemon_running
        
        if not daemon_running:
            # Try to start daemon
            if self.start_daemon():
                result['daemon_running'] = True
                daemon_running = True
        
        # Test RPC connection
        if daemon_running:
            try:
                version_info = self.get_version()
                result['rpc_status'] = version_info is not None
                if version_info:
                    result['rpc_version'] = version_info.get('version', 'unknown')
            except:
                result['rpc_status'] = False
        
        return result

# Global aria2 service instance
aria2_service = Aria2Service()


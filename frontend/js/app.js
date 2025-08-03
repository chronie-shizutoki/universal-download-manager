/**
 * Main Application Controller
 */
class App {
    constructor() {
        this.refreshInterval = null;
        this.websocket = null;
        this.isOnline = navigator.onLine;
        
        this.init();
    }
    
    async init() {
        // Wait for i18n to initialize
        if (window.i18n) {
            await new Promise(resolve => {
                if (window.i18n.currentLanguage) {
                    resolve();
                } else {
                    window.addEventListener('languageChanged', resolve, { once: true });
                }
            });
        }
        
        this.initEventListeners();
        this.initForms();
        this.initWebSocket();
        this.startPeriodicRefresh();
        
        // Initial data load
        await this.loadInitialData();
    }
    
    initEventListeners() {
        // System test button
        const testSystemBtn = document.getElementById('testSystemBtn');
        if (testSystemBtn) {
            testSystemBtn.addEventListener('click', () => this.testSystem());
        }
        
        // Refresh buttons
        const refreshProgressBtn = document.getElementById('refreshProgressBtn');
        const refreshFilesBtn = document.getElementById('refreshFilesBtn');
        
        if (refreshProgressBtn) {
            refreshProgressBtn.addEventListener('click', () => this.loadProgress());
        }
        
        if (refreshFilesBtn) {
            refreshFilesBtn.addEventListener('click', () => this.loadFiles());
        }
        
        // Batch add button
        const batchAddBtn = document.getElementById('batchAddBtn');
        if (batchAddBtn) {
            batchAddBtn.addEventListener('click', () => this.handleBatchAdd());
        }
        
        // Online/offline detection
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.handleOnlineStatus();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.handleOnlineStatus();
        });
        
        // Language change handler
        window.addEventListener('languageChanged', () => {
            this.refreshUI();
        });
        
        // WebSocket event handlers
        if (window.api) {
            window.api.addEventListener('websocket:connected', () => {
                console.log('WebSocket connected');
                this.stopPeriodicRefresh(); // Use WebSocket instead of polling
            });
            
            window.api.addEventListener('websocket:disconnected', () => {
                console.log('WebSocket disconnected');
                this.startPeriodicRefresh(); // Fallback to polling
            });
            
            window.api.addEventListener('websocket:progress_update', (data) => {
                this.handleProgressUpdate(data);
            });
            
            window.api.addEventListener('websocket:download_complete', (data) => {
                this.handleDownloadComplete(data);
            });
        }
    }
    
    initForms() {
        // URL form
        const urlForm = document.getElementById('urlForm');
        if (urlForm) {
            urlForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleUrlSubmit();
            });
        }
        
        // Magnet form
        const magnetForm = document.getElementById('magnetForm');
        if (magnetForm) {
            magnetForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleMagnetSubmit();
            });
        }
    }
    
    initWebSocket() {
        if (window.api && typeof window.api.connectWebSocket === 'function') {
            try {
                this.websocket = window.api.connectWebSocket();
            } catch (error) {
                console.warn('Failed to initialize WebSocket:', error);
                // Continue with polling fallback
            }
        }
    }
    
    startPeriodicRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        // Refresh every 3 seconds
        this.refreshInterval = setInterval(() => {
            if (this.isOnline) {
                this.loadProgress();
            }
        }, 3000);
    }
    
    stopPeriodicRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    async loadInitialData() {
        try {
            await Promise.all([
                this.testSystem(),
                this.loadProgress(),
                this.loadFiles()
            ]);
        } catch (error) {
            console.error('Failed to load initial data:', error);
            if (window.ui) {
                window.ui.showToast('Failed to load initial data', 'error');
            }
        }
    }
    
    async testSystem() {
        try {
            const result = await window.api.testSystem();
            
            let message = '';
            let type = 'success';
            
            if (result.aria2c_available) {
                const rpcStatus = result.rpc_status ? 
                    '✓ RPC connection normal' : 
                    '✗ RPC connection failed';
                message = `✓ aria2c available: ${result.version}<br>${rpcStatus}`;
                
                if (!result.rpc_status) {
                    type = 'warning';
                }
            } else {
                message = `✗ aria2c not available: ${result.error}`;
                type = 'error';
            }
            
            if (window.ui) {
                window.ui.showStatus('systemStatus', message, type);
            }
            
            return result;
        } catch (error) {
            const message = `✗ System test failed: ${error.message}`;
            if (window.ui) {
                window.ui.showStatus('systemStatus', message, 'error');
            }
            throw error;
        }
    }
    
    async loadProgress() {
        if (!this.isOnline) return;
        
        try {
            if (window.ui) {
                window.ui.showLoading('progressLoading');
            }
            
            const result = await window.api.getDownloads();
            
            if (window.ui) {
                window.ui.hideLoading('progressLoading');
                
                if (result.error) {
                    window.ui.showStatus('downloadProgress', 
                        `Failed to get progress: ${result.error}`, 'error');
                } else {
                    window.ui.updateDownloadsList(result.downloads || []);
                }
            }
        } catch (error) {
            if (window.ui) {
                window.ui.hideLoading('progressLoading');
                window.ui.showStatus('downloadProgress', 
                    `Failed to get progress: ${error.message}`, 'error');
            }
        }
    }
    
    async loadFiles() {
        if (!this.isOnline) return;
        
        try {
            if (window.ui) {
                window.ui.showLoading('filesLoading');
            }
            
            const result = await window.api.getFiles();
            
            if (window.ui) {
                window.ui.hideLoading('filesLoading');
                
                if (result.error) {
                    window.ui.showStatus('filesList', 
                        `Failed to get files: ${result.error}`, 'error');
                } else {
                    window.ui.updateFilesList(result.files || []);
                }
            }
        } catch (error) {
            if (window.ui) {
                window.ui.hideLoading('filesLoading');
                window.ui.showStatus('filesList', 
                    `Failed to get files: ${error.message}`, 'error');
            }
        }
    }
    
    async handleUrlSubmit() {
        const urlInput = document.getElementById('urlInput');
        if (!urlInput) return;
        
        const url = urlInput.value.trim();
        if (!url) return;
        
        try {
            if (window.ui) {
                window.ui.showStatus('addStatus', 
                    window.i18n.t('ui.loading'), 'info');
            }
            
            const result = await window.api.addUrl(url);
            
            if (result.error) {
                if (window.ui) {
                    window.ui.showStatus('addStatus', 
                        `${window.i18n.t('messages.download_failed')}: ${result.error}`, 'error');
                }
            } else {
                if (window.ui) {
                    window.ui.showStatus('addStatus', 
                        `${window.i18n.t('messages.download_started')} (ID: ${result.task_id})`, 'success');
                }
                
                urlInput.value = '';
                
                // Refresh progress after 2 seconds
                setTimeout(() => this.loadProgress(), 2000);
            }
        } catch (error) {
            if (window.ui) {
                window.ui.showStatus('addStatus', 
                    `${window.i18n.t('messages.download_failed')}: ${error.message}`, 'error');
            }
        }
    }
    
    async handleMagnetSubmit() {
        const magnetInput = document.getElementById('magnetInput');
        if (!magnetInput) return;
        
        const magnet = magnetInput.value.trim();
        if (!magnet) return;
        
        if (!magnet.startsWith('magnet:')) {
            if (window.ui) {
                window.ui.showStatus('addStatus', 
                    window.i18n.t('messages.invalid_magnet'), 'error');
            }
            return;
        }
        
        try {
            if (window.ui) {
                window.ui.showStatus('addStatus', 
                    window.i18n.t('ui.loading'), 'info');
            }
            
            const result = await window.api.addMagnet(magnet);
            
            if (result.error) {
                if (window.ui) {
                    window.ui.showStatus('addStatus', 
                        `${window.i18n.t('messages.download_failed')}: ${result.error}`, 'error');
                }
            } else {
                if (window.ui) {
                    window.ui.showStatus('addStatus', 
                        `${window.i18n.t('messages.download_started')} (ID: ${result.task_id})`, 'success');
                }
                
                magnetInput.value = '';
                
                // Refresh progress after 2 seconds
                setTimeout(() => this.loadProgress(), 2000);
            }
        } catch (error) {
            if (window.ui) {
                window.ui.showStatus('addStatus', 
                    `${window.i18n.t('messages.download_failed')}: ${error.message}`, 'error');
            }
        }
    }
    
    async handleBatchAdd() {
        const batchUrls = document.getElementById('batchUrls');
        if (!batchUrls) return;
        
        const text = batchUrls.value.trim();
        if (!text) return;
        
        const urls = text.split('\n')
            .map(line => line.trim())
            .filter(line => line && !line.startsWith('#'));
        
        if (urls.length === 0) {
            if (window.ui) {
                window.ui.showStatus('addStatus', 
                    window.i18n.t('messages.no_urls_found'), 'error');
            }
            return;
        }
        
        try {
            if (window.ui) {
                window.ui.showStatus('addStatus', 
                    window.i18n.t('ui.loading'), 'info');
            }
            
            const result = await window.api.addBatchUrls(urls);
            
            if (result.error) {
                if (window.ui) {
                    window.ui.showStatus('addStatus', 
                        `${window.i18n.t('messages.download_failed')}: ${result.error}`, 'error');
                }
            } else {
                const successCount = result.success_count || 0;
                const failCount = result.fail_count || 0;
                
                let message = `${successCount} downloads started`;
                if (failCount > 0) {
                    message += `, ${failCount} failed`;
                }
                
                if (window.ui) {
                    window.ui.showStatus('addStatus', message, 
                        failCount > 0 ? 'warning' : 'success');
                }
                
                batchUrls.value = '';
                
                // Refresh progress after 2 seconds
                setTimeout(() => this.loadProgress(), 2000);
            }
        } catch (error) {
            if (window.ui) {
                window.ui.showStatus('addStatus', 
                    `${window.i18n.t('messages.download_failed')}: ${error.message}`, 'error');
            }
        }
    }
    
    handleProgressUpdate(data) {
        // Handle real-time progress updates from WebSocket
        if (data.downloads && window.ui) {
            window.ui.updateDownloadsList(data.downloads);
        }
    }
    
    handleDownloadComplete(data) {
        // Handle download completion notification
        if (window.ui) {
            window.ui.showToast(
                `Download completed: ${data.file_name}`, 
                'success'
            );
        }
        
        // Refresh files list
        this.loadFiles();
    }
    
    handleOnlineStatus() {
        if (this.isOnline) {
            // Reconnect WebSocket if needed
            if (!this.websocket || this.websocket.readyState === WebSocket.CLOSED) {
                this.initWebSocket();
            }
            
            // Reload data
            this.loadInitialData();
            
            if (window.ui) {
                window.ui.showToast('Connection restored', 'success');
            }
        } else {
            if (window.ui) {
                window.ui.showToast('Connection lost - working offline', 'warning');
            }
        }
    }
    
    refreshUI() {
        // Refresh UI elements after language change
        setTimeout(() => {
            this.loadProgress();
            this.loadFiles();
        }, 100);
    }
    
    // Cleanup method
    destroy() {
        this.stopPeriodicRefresh();
        
        if (this.websocket) {
            this.websocket.close();
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.app) {
        window.app.destroy();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = App;
}


/**
 * UI Components and Interactions
 */
class UI {
    constructor() {
        this.currentTheme = 'light';
        this.activeTab = 'url';
        this.downloads = new Map();
        this.files = [];
        this.filters = {
            status: '',
            category: ''
        };
        
        this.init();
    }
    
    init() {
        this.loadTheme();
        this.initEventListeners();
        this.initDragAndDrop();
        this.initTabs();
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.setTheme(savedTheme);
    }
    
    setTheme(theme) {
        this.currentTheme = theme;
        document.body.className = `${theme}-theme`;
        localStorage.setItem('theme', theme);
        
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            const icon = themeToggle.querySelector('i');
            icon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    }
    
    initEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.setTheme(this.currentTheme === 'light' ? 'dark' : 'light');
            });
        }
        
        // Language selector
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                if (window.i18n) {
                    window.i18n.setLanguage(e.target.value);
                }
            });
        }
        
        // Filter controls
        const statusFilter = document.getElementById('statusFilter');
        const categoryFilter = document.getElementById('categoryFilter');
        
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.filters.status = e.target.value;
                this.filterDownloads();
            });
        }
        
        if (categoryFilter) {
            categoryFilter.addEventListener('change', (e) => {
                this.filters.category = e.target.value;
                this.filterDownloads();
            });
        }
        
        // Modal close
        const modal = document.getElementById('confirmModal');
        const modalClose = modal?.querySelector('.modal-close');
        const confirmCancel = document.getElementById('confirmCancel');
        
        if (modalClose) {
            modalClose.addEventListener('click', () => this.hideModal());
        }
        
        if (confirmCancel) {
            confirmCancel.addEventListener('click', () => this.hideModal());
        }
        
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal();
                }
            });
        }
        
        // File input handlers
        const torrentFile = document.getElementById('torrentFile');
        const urlListFile = document.getElementById('urlListFile');
        
        if (torrentFile) {
            torrentFile.addEventListener('change', (e) => {
                this.handleTorrentFiles(e.target.files);
            });
        }
        
        if (urlListFile) {
            urlListFile.addEventListener('change', (e) => {
                this.handleUrlListFile(e.target.files[0]);
            });
        }
    }
    
    initDragAndDrop() {
        const torrentUpload = document.getElementById('torrentUpload');
        const urlListUpload = document.getElementById('urlListUpload');
        
        if (torrentUpload) {
            this.setupDragAndDrop(torrentUpload, (files) => {
                const torrentFiles = Array.from(files).filter(file => 
                    file.name.toLowerCase().endsWith('.torrent')
                );
                if (torrentFiles.length > 0) {
                    this.handleTorrentFiles(torrentFiles);
                }
            });
        }
        
        if (urlListUpload) {
            this.setupDragAndDrop(urlListUpload, (files) => {
                const textFiles = Array.from(files).filter(file => 
                    file.type === 'text/plain' || file.name.toLowerCase().endsWith('.txt')
                );
                if (textFiles.length > 0) {
                    this.handleUrlListFile(textFiles[0]);
                }
            });
        }
    }
    
    setupDragAndDrop(element, onDrop) {
        element.addEventListener('dragover', (e) => {
            e.preventDefault();
            element.classList.add('dragover');
        });
        
        element.addEventListener('dragleave', (e) => {
            e.preventDefault();
            element.classList.remove('dragover');
        });
        
        element.addEventListener('drop', (e) => {
            e.preventDefault();
            element.classList.remove('dragover');
            onDrop(e.dataTransfer.files);
        });
    }
    
    initTabs() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        const tabPanes = document.querySelectorAll('.tab-pane');
        
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.getAttribute('data-tab');
                this.switchTab(tabId);
            });
        });
    }
    
    switchTab(tabId) {
        this.activeTab = tabId;
        
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
        });
        
        // Update tab panes
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.toggle('active', pane.id === `${tabId}-tab`);
        });
    }
    
    async handleTorrentFiles(files) {
        for (const file of files) {
            try {
                this.showStatus('addStatus', window.i18n.t('ui.loading'), 'info');
                await window.api.uploadTorrent(file);
                this.showStatus('addStatus', 
                    window.i18n.t('messages.download_started'), 'success');
            } catch (error) {
                this.showStatus('addStatus', 
                    `${window.i18n.t('messages.download_failed')}: ${error.message}`, 'error');
            }
        }
    }
    
    async handleUrlListFile(file) {
        try {
            const text = await file.text();
            const urls = text.split('\n')
                .map(line => line.trim())
                .filter(line => line && !line.startsWith('#'));
            
            const batchUrls = document.getElementById('batchUrls');
            if (batchUrls) {
                batchUrls.value = urls.join('\n');
            }
        } catch (error) {
            this.showStatus('addStatus', 
                `${window.i18n.t('errors.file_not_found')}: ${error.message}`, 'error');
        }
    }
    
    showStatus(elementId, message, type = 'info') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        element.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            element.innerHTML = '';
        }, 5000);
    }
    
    showToast(message, type = 'info', duration = 5000) {
        const container = document.getElementById('toastContainer');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, duration);
    }
    
    showModal(message, onConfirm) {
        const modal = document.getElementById('confirmModal');
        const messageElement = document.getElementById('confirmMessage');
        const confirmOk = document.getElementById('confirmOk');
        
        if (!modal || !messageElement || !confirmOk) return;
        
        messageElement.textContent = message;
        modal.classList.add('active');
        
        // Remove existing listeners
        const newConfirmOk = confirmOk.cloneNode(true);
        confirmOk.parentNode.replaceChild(newConfirmOk, confirmOk);
        
        // Add new listener
        newConfirmOk.addEventListener('click', () => {
            this.hideModal();
            if (onConfirm) onConfirm();
        });
    }
    
    hideModal() {
        const modal = document.getElementById('confirmModal');
        if (modal) {
            modal.classList.remove('active');
        }
    }
    
    updateDownloadsList(downloads) {
        this.downloads.clear();
        downloads.forEach(download => {
            this.downloads.set(download.gid, download);
        });
        
        this.renderDownloads();
    }
    
    renderDownloads() {
        const container = document.getElementById('downloadProgress');
        if (!container) return;
        
        const filteredDownloads = this.getFilteredDownloads();
        
        if (filteredDownloads.length === 0) {
            container.innerHTML = `
                <div class="status-message status-info">
                    ${window.i18n.t('ui.no_downloads')}
                </div>
            `;
            return;
        }
        
        container.innerHTML = filteredDownloads.map(download => 
            this.createDownloadItemHTML(download)
        ).join('');
        
        // Add event listeners to download controls
        this.attachDownloadEventListeners();
    }
    
    getFilteredDownloads() {
        let downloads = Array.from(this.downloads.values());
        
        if (this.filters.status) {
            downloads = downloads.filter(d => d.status === this.filters.status);
        }
        
        if (this.filters.category) {
            downloads = downloads.filter(d => d.category === this.filters.category);
        }
        
        return downloads;
    }
    
    createDownloadItemHTML(download) {
        const statusText = window.i18n.t(`status.${download.status}`);
        const categoryText = window.i18n.t(`categories.${download.category}`);
        
        return `
            <div class="download-item" data-gid="${download.gid}">
                <div class="download-header">
                    <div class="download-info">
                        <div class="download-name" title="${download.file_name}">
                            ${download.file_name || window.i18n.t('ui.unknown')}
                        </div>
                        <div class="download-url" title="${download.url}">
                            ${this.truncateUrl(download.url)}
                        </div>
                    </div>
                    <div class="download-status status-${download.status}">
                        ${statusText}
                    </div>
                </div>
                
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${download.progress}%"></div>
                    </div>
                    <div class="progress-text">
                        <span>${download.progress}%</span>
                        <span>${download.formatted_completed} / ${download.formatted_total}</span>
                    </div>
                </div>
                
                <div class="download-stats">
                    <div class="stat-item">
                        <div class="stat-value">${download.formatted_speed}</div>
                        <div class="stat-label">${window.i18n.t('ui.download_speed')}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${download.eta}</div>
                        <div class="stat-label">${window.i18n.t('ui.eta')}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${download.connections}</div>
                        <div class="stat-label">${window.i18n.t('ui.connections')}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${download.num_seeders}</div>
                        <div class="stat-label">${window.i18n.t('ui.seeders')}</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${categoryText}</div>
                        <div class="stat-label">${window.i18n.t('ui.category')}</div>
                    </div>
                </div>
                
                <div class="download-controls">
                    ${this.createDownloadControlsHTML(download)}
                </div>
            </div>
        `;
    }
    
    createDownloadControlsHTML(download) {
        const controls = [];
        
        if (download.status === 'active') {
            controls.push(`
                <button class="btn btn-warning btn-sm" data-action="pause" data-gid="${download.gid}">
                    <i class="fas fa-pause"></i> ${window.i18n.t('ui.pause')}
                </button>
            `);
        } else if (download.status === 'paused') {
            controls.push(`
                <button class="btn btn-success btn-sm" data-action="resume" data-gid="${download.gid}">
                    <i class="fas fa-play"></i> ${window.i18n.t('ui.resume')}
                </button>
            `);
        } else if (download.status === 'error') {
            controls.push(`
                <button class="btn btn-primary btn-sm" data-action="retry" data-gid="${download.gid}">
                    <i class="fas fa-redo"></i> Retry
                </button>
            `);
        }
        
        controls.push(`
            <button class="btn btn-danger btn-sm" data-action="remove" data-gid="${download.gid}">
                <i class="fas fa-trash"></i> ${window.i18n.t('ui.remove')}
            </button>
        `);
        
        return controls.join('');
    }
    
    attachDownloadEventListeners() {
        const buttons = document.querySelectorAll('.download-controls button[data-action]');
        buttons.forEach(button => {
            button.addEventListener('click', async (e) => {
                const action = e.currentTarget.getAttribute('data-action');
                const gid = e.currentTarget.getAttribute('data-gid');
                
                if (action === 'remove') {
                    this.showModal(
                        window.i18n.t('ui.confirm_remove'),
                        () => this.handleDownloadAction(action, gid)
                    );
                } else {
                    await this.handleDownloadAction(action, gid);
                }
            });
        });
    }
    
    async handleDownloadAction(action, gid) {
        try {
            switch (action) {
                case 'pause':
                    await window.api.pauseDownload(gid);
                    this.showToast(window.i18n.t('messages.download_paused'), 'success');
                    break;
                case 'resume':
                    await window.api.resumeDownload(gid);
                    this.showToast(window.i18n.t('messages.download_resumed'), 'success');
                    break;
                case 'remove':
                    await window.api.removeDownload(gid);
                    this.showToast(window.i18n.t('messages.download_removed'), 'success');
                    break;
                case 'retry':
                    await window.api.retryDownload(gid);
                    this.showToast(window.i18n.t('messages.download_started'), 'success');
                    break;
            }
        } catch (error) {
            this.showToast(`${window.i18n.t('messages.download_failed')}: ${error.message}`, 'error');
        }
    }
    
    updateFilesList(files) {
        this.files = files;
        this.renderFiles();
    }
    
    renderFiles() {
        const container = document.getElementById('filesList');
        if (!container) return;
        
        if (this.files.length === 0) {
            container.innerHTML = `
                <div class="status-message status-info">
                    ${window.i18n.t('ui.no_files')}
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.files.map(file => 
            this.createFileItemHTML(file)
        ).join('');
        
        // Add event listeners to file actions
        this.attachFileEventListeners();
    }
    
    createFileItemHTML(file) {
        const icon = this.getFileIcon(file.name);
        
        return `
            <div class="file-item">
                <div class="file-header">
                    <i class="file-icon ${icon}"></i>
                    <div class="file-info">
                        <div class="file-name" title="${file.name}">${file.name}</div>
                        <div class="file-size">${file.formatted_size || this.formatSize(file.size)}</div>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-primary btn-sm" data-action="download" data-filename="${file.name}">
                        <i class="fas fa-download"></i> Download
                    </button>
                    <button class="btn btn-danger btn-sm" data-action="delete" data-filename="${file.name}">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }
    
    attachFileEventListeners() {
        const buttons = document.querySelectorAll('.file-actions button[data-action]');
        buttons.forEach(button => {
            button.addEventListener('click', async (e) => {
                const action = e.currentTarget.getAttribute('data-action');
                const filename = e.currentTarget.getAttribute('data-filename');
                
                if (action === 'delete') {
                    this.showModal(
                        `Are you sure you want to delete "${filename}"?`,
                        () => this.handleFileAction(action, filename)
                    );
                } else {
                    await this.handleFileAction(action, filename);
                }
            });
        });
    }
    
    async handleFileAction(action, filename) {
        try {
            switch (action) {
                case 'download':
                    await window.api.downloadFile(filename);
                    break;
                case 'delete':
                    await window.api.deleteFile(filename);
                    this.showToast('File deleted successfully', 'success');
                    // Refresh file list
                    if (window.app) {
                        window.app.loadFiles();
                    }
                    break;
            }
        } catch (error) {
            this.showToast(`Action failed: ${error.message}`, 'error');
        }
    }
    
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        
        const iconMap = {
            // Video
            'mp4': 'fas fa-file-video',
            'avi': 'fas fa-file-video',
            'mkv': 'fas fa-file-video',
            'mov': 'fas fa-file-video',
            'wmv': 'fas fa-file-video',
            'flv': 'fas fa-file-video',
            'webm': 'fas fa-file-video',
            
            // Audio
            'mp3': 'fas fa-file-audio',
            'wav': 'fas fa-file-audio',
            'flac': 'fas fa-file-audio',
            'aac': 'fas fa-file-audio',
            'ogg': 'fas fa-file-audio',
            
            // Image
            'jpg': 'fas fa-file-image',
            'jpeg': 'fas fa-file-image',
            'png': 'fas fa-file-image',
            'gif': 'fas fa-file-image',
            'bmp': 'fas fa-file-image',
            'svg': 'fas fa-file-image',
            
            // Document
            'pdf': 'fas fa-file-pdf',
            'doc': 'fas fa-file-word',
            'docx': 'fas fa-file-word',
            'txt': 'fas fa-file-alt',
            'rtf': 'fas fa-file-alt',
            
            // Archive
            'zip': 'fas fa-file-archive',
            'rar': 'fas fa-file-archive',
            '7z': 'fas fa-file-archive',
            'tar': 'fas fa-file-archive',
            'gz': 'fas fa-file-archive',
            
            // Software
            'exe': 'fas fa-file-code',
            'msi': 'fas fa-file-code',
            'deb': 'fas fa-file-code',
            'rpm': 'fas fa-file-code'
        };
        
        return iconMap[ext] || 'fas fa-file';
    }
    
    formatSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    truncateUrl(url, maxLength = 50) {
        if (url.length <= maxLength) return url;
        return url.substring(0, maxLength - 3) + '...';
    }
    
    filterDownloads() {
        this.renderDownloads();
    }
    
    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.remove('hidden');
        }
    }
    
    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.classList.add('hidden');
        }
    }
}

// Create global UI instance
window.ui = new UI();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UI;
}


/**
 * API Client for Universal Download Manager
 */
class ApiClient {
    constructor() {
        this.baseUrl = '/api/v1';
        this.timeout = 30000; // 30 seconds
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            timeout: this.timeout,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        // Add language header
        if (window.i18n) {
            config.headers['Accept-Language'] = window.i18n.getCurrentLanguage();
        }
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), config.timeout);
            
            const response = await fetch(url, {
                ...config,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }
    
    async get(endpoint, params = {}) {
        const url = new URL(endpoint, window.location.origin + this.baseUrl);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });
        
        return this.request(url.pathname + url.search, {
            method: 'GET'
        });
    }
    
    async post(endpoint, data = {}, options = {}) {
        const config = {
            method: 'POST',
            ...options
        };
        
        if (data instanceof FormData) {
            // Remove Content-Type header for FormData (browser will set it with boundary)
            delete config.headers?.['Content-Type'];
            config.body = data;
        } else {
            config.body = JSON.stringify(data);
        }
        
        return this.request(endpoint, config);
    }
    
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
    
    // System API
    async testSystem() {
        return this.get('/system/test');
    }
    
    // Download API
    async addDownload(data) {
        return this.post('/downloads', data);
    }
    
    async addMagnet(magnetUrl) {
        return this.post('/downloads/magnet', { url: magnetUrl });
    }
    
    async addUrl(url) {
        return this.post('/downloads/url', { url });
    }
    
    async uploadTorrent(file) {
        const formData = new FormData();
        formData.append('torrent', file);
        return this.post('/downloads/torrent', formData);
    }
    
    async addBatchUrls(urls) {
        return this.post('/downloads/batch', { urls });
    }
    
    async getDownloads(filters = {}) {
        return this.get('/downloads', filters);
    }
    
    async getDownload(gid) {
        return this.get(`/downloads/${gid}`);
    }
    
    async pauseDownload(gid) {
        return this.post(`/downloads/${gid}/pause`);
    }
    
    async resumeDownload(gid) {
        return this.post(`/downloads/${gid}/resume`);
    }
    
    async removeDownload(gid) {
        return this.delete(`/downloads/${gid}`);
    }
    
    async retryDownload(gid) {
        return this.post(`/downloads/${gid}/retry`);
    }
    
    // Files API
    async getFiles() {
        return this.get('/files');
    }
    
    async downloadFile(filename) {
        const url = `${this.baseUrl}/files/${encodeURIComponent(filename)}/download`;
        window.open(url, '_blank');
    }
    
    async deleteFile(filename) {
        return this.delete(`/files/${encodeURIComponent(filename)}`);
    }
    
    // Settings API
    async getSettings() {
        return this.get('/settings');
    }
    
    async updateSettings(settings) {
        return this.put('/settings', settings);
    }
    
    // I18n API
    async getTranslations(language) {
        return this.get(`/i18n/${language}`);
    }
    
    async getAvailableLanguages() {
        return this.get('/i18n/languages');
    }
    
    // Statistics API
    async getStatistics() {
        return this.get('/statistics');
    }
    
    // WebSocket connection for real-time updates
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        const ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            console.log('WebSocket connected');
            this.dispatchEvent('websocket:connected');
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.dispatchEvent('websocket:message', data);
                
                // Dispatch specific events based on message type
                if (data.type) {
                    this.dispatchEvent(`websocket:${data.type}`, data);
                }
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };
        
        ws.onclose = (event) => {
            console.log('WebSocket disconnected:', event.code, event.reason);
            this.dispatchEvent('websocket:disconnected', { code: event.code, reason: event.reason });
            
            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
                console.log('Attempting to reconnect WebSocket...');
                this.connectWebSocket();
            }, 5000);
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.dispatchEvent('websocket:error', error);
        };
        
        return ws;
    }
    
    // Event system for API events
    addEventListener(event, callback) {
        if (!this.eventListeners) {
            this.eventListeners = {};
        }
        
        if (!this.eventListeners[event]) {
            this.eventListeners[event] = [];
        }
        
        this.eventListeners[event].push(callback);
    }
    
    removeEventListener(event, callback) {
        if (!this.eventListeners || !this.eventListeners[event]) {
            return;
        }
        
        const index = this.eventListeners[event].indexOf(callback);
        if (index > -1) {
            this.eventListeners[event].splice(index, 1);
        }
    }
    
    dispatchEvent(event, data = null) {
        if (!this.eventListeners || !this.eventListeners[event]) {
            return;
        }
        
        this.eventListeners[event].forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`Error in event listener for ${event}:`, error);
            }
        });
    }
}

// Create global API client instance
window.api = new ApiClient();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApiClient;
}


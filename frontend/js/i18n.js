/**
 * Frontend Internationalization Module
 */
class I18n {
    constructor() {
        this.currentLanguage = 'en';
        this.translations = {};
        this.fallbackLanguage = 'en';
        this.availableLanguages = {
            'en': 'English',
            'zh': '中文',
            'ja': '日本語'
        };
        
        this.init();
    }
    
    async init() {
        // Load saved language preference
        const savedLanguage = localStorage.getItem('language') || 'en';
        await this.setLanguage(savedLanguage);
        
        // Update language selector
        this.updateLanguageSelector();
        
        // Apply translations to existing elements
        this.applyTranslations();
    }
    
    async loadTranslations(language) {
        if (this.translations[language]) {
            return this.translations[language];
        }
        
        try {
            const response = await fetch(`/api/v1/i18n/${language}`);
            if (response.ok) {
                const translations = await response.json();
                this.translations[language] = translations;
                return translations;
            }
        } catch (error) {
            console.warn(`Failed to load translations for ${language}:`, error);
        }
        
        // Fallback translations
        const fallbackTranslations = await this.getFallbackTranslations(language);
        this.translations[language] = fallbackTranslations;
        return fallbackTranslations;
    }
    
    async getFallbackTranslations(language) {
        // Fallback translations embedded in frontend
        const fallbackTranslations = {
            'en': {
                'app.title': 'Universal Download Manager',
                'app.subtitle': 'Multi-protocol download tool with aria2c',
                'ui.add_download': 'Add Download',
                'ui.start_download': 'Start Download',
                'ui.pause': 'Pause',
                'ui.resume': 'Resume',
                'ui.remove': 'Remove',
                'ui.refresh': 'Refresh',
                'ui.test_system': 'Test System',
                'ui.download_progress': 'Download Progress',
                'ui.downloaded_files': 'Downloaded Files',
                'ui.system_status': 'System Status',
                'ui.loading': 'Loading...',
                'ui.batch_add': 'Batch Add',
                'ui.magnet_link': 'Magnet Link',
                'ui.http_url': 'HTTP/HTTPS URL',
                'ui.upload_torrent': 'Upload Torrent File',
                'ui.drag_drop_hint': 'Drag and drop files here or click to browse',
                'status.waiting': 'Waiting',
                'status.active': 'Downloading',
                'status.paused': 'Paused',
                'status.complete': 'Completed',
                'status.error': 'Error',
                'categories.video': 'Video',
                'categories.audio': 'Audio',
                'categories.image': 'Image',
                'categories.document': 'Document',
                'categories.archive': 'Archive',
                'categories.software': 'Software',
                'categories.other': 'Other'
            },
            'zh': {
                'app.title': '通用下载管理器',
                'app.subtitle': '基于aria2c的多协议下载工具',
                'ui.add_download': '添加下载',
                'ui.start_download': '开始下载',
                'ui.pause': '暂停',
                'ui.resume': '继续',
                'ui.remove': '删除',
                'ui.refresh': '刷新',
                'ui.test_system': '测试系统',
                'ui.download_progress': '下载进度',
                'ui.downloaded_files': '已下载文件',
                'ui.system_status': '系统状态',
                'ui.loading': '加载中...',
                'ui.batch_add': '批量添加',
                'ui.magnet_link': '磁力链接',
                'ui.http_url': 'HTTP/HTTPS链接',
                'ui.upload_torrent': '上传种子文件',
                'ui.drag_drop_hint': '拖拽文件到此处或点击浏览',
                'status.waiting': '等待中',
                'status.active': '下载中',
                'status.paused': '已暂停',
                'status.complete': '已完成',
                'status.error': '错误',
                'categories.video': '视频',
                'categories.audio': '音频',
                'categories.image': '图片',
                'categories.document': '文档',
                'categories.archive': '压缩包',
                'categories.software': '软件',
                'categories.other': '其他'
            },
            'ja': {
                'app.title': 'ユニバーサルダウンロードマネージャー',
                'app.subtitle': 'aria2cベースのマルチプロトコルダウンロードツール',
                'ui.add_download': 'ダウンロード追加',
                'ui.start_download': 'ダウンロード開始',
                'ui.pause': '一時停止',
                'ui.resume': '再開',
                'ui.remove': '削除',
                'ui.refresh': '更新',
                'ui.test_system': 'システムテスト',
                'ui.download_progress': 'ダウンロード進行状況',
                'ui.downloaded_files': 'ダウンロード済みファイル',
                'ui.system_status': 'システム状態',
                'ui.loading': '読み込み中...',
                'ui.batch_add': '一括追加',
                'ui.magnet_link': 'マグネットリンク',
                'ui.http_url': 'HTTP/HTTPSリンク',
                'ui.upload_torrent': 'トレントファイルアップロード',
                'ui.drag_drop_hint': 'ファイルをここにドラッグ＆ドロップするか、クリックして参照',
                'status.waiting': '待機中',
                'status.active': 'ダウンロード中',
                'status.paused': '一時停止',
                'status.complete': '完了',
                'status.error': 'エラー',
                'categories.video': '動画',
                'categories.audio': '音声',
                'categories.image': '画像',
                'categories.document': '文書',
                'categories.archive': 'アーカイブ',
                'categories.software': 'ソフトウェア',
                'categories.other': 'その他'
            }
        };
        
        return fallbackTranslations[language] || fallbackTranslations[this.fallbackLanguage];
    }
    
    async setLanguage(language) {
        if (!this.availableLanguages[language]) {
            language = this.fallbackLanguage;
        }
        
        this.currentLanguage = language;
        await this.loadTranslations(language);
        
        // Save preference
        localStorage.setItem('language', language);
        
        // Update document language
        document.documentElement.lang = language;
        
        // Apply translations
        this.applyTranslations();
        
        // Dispatch language change event
        window.dispatchEvent(new CustomEvent('languageChanged', {
            detail: { language }
        }));
    }
    
    translate(key, variables = {}) {
        const translations = this.translations[this.currentLanguage] || {};
        let translation = this.getNestedValue(translations, key);
        
        // Fallback to default language
        if (!translation && this.currentLanguage !== this.fallbackLanguage) {
            const fallbackTranslations = this.translations[this.fallbackLanguage] || {};
            translation = this.getNestedValue(fallbackTranslations, key);
        }
        
        // Return key if no translation found
        if (!translation) {
            return key;
        }
        
        // Replace variables
        return this.replaceVariables(translation, variables);
    }
    
    getNestedValue(obj, key) {
        return key.split('.').reduce((current, keyPart) => {
            return current && current[keyPart] !== undefined ? current[keyPart] : null;
        }, obj);
    }
    
    replaceVariables(text, variables) {
        return text.replace(/\{(\w+)\}/g, (match, key) => {
            return variables[key] !== undefined ? variables[key] : match;
        });
    }
    
    applyTranslations() {
        // Translate elements with data-i18n attribute
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            const translation = this.translate(key);
            
            if (element.tagName === 'INPUT' && (element.type === 'text' || element.type === 'url')) {
                element.placeholder = translation;
            } else if (element.tagName === 'TEXTAREA') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        });
        
        // Update page title
        const titleElement = document.querySelector('title');
        if (titleElement) {
            titleElement.textContent = this.translate('app.title');
        }
    }
    
    updateLanguageSelector() {
        const languageSelect = document.getElementById('languageSelect');
        if (languageSelect) {
            languageSelect.value = this.currentLanguage;
        }
    }
    
    getAvailableLanguages() {
        return this.availableLanguages;
    }
    
    getCurrentLanguage() {
        return this.currentLanguage;
    }
    
    // Shorthand method
    t(key, variables = {}) {
        return this.translate(key, variables);
    }
}

// Create global i18n instance
window.i18n = new I18n();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = I18n;
}


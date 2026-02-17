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
        
        // Start with fallback translations
        const fallbackTranslations = this.getFallbackTranslations(language);
        let mergedTranslations = { ...fallbackTranslations };
        
        try {
            const response = await fetch(`/api/v1/i18n/${language}`);
            if (response.ok) {
                const apiTranslations = await response.json();
                // Merge API translations with fallback (API takes precedence)
                mergedTranslations = { ...fallbackTranslations, ...this.flattenTranslations(apiTranslations) };
            }
        } catch (error) {
            console.warn(`Failed to load translations for ${language}:`, error);
        }
        
        this.translations[language] = mergedTranslations;
        return mergedTranslations;
    }
    
    flattenTranslations(obj, prefix = '') {
        let result = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                const newKey = prefix ? `${prefix}.${key}` : key;
                if (typeof obj[key] === 'object' && obj[key] !== null && !Array.isArray(obj[key])) {
                    Object.assign(result, this.flattenTranslations(obj[key], newKey));
                } else {
                    result[newKey] = obj[key];
                }
            }
        }
        return result;
    }
    
    getFallbackTranslations(language) {
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
                'ui.or_upload_urls': 'Or upload a text file with URLs',
                'ui.upload_file': 'Upload File',
                'ui.urls_per_line': 'URLs (one per line)',
                'ui.download': 'Download',
                'ui.delete': 'Delete',
                'ui.no_downloads': 'No downloads',
                'ui.no_files': 'No files',
                'ui.unknown': 'Unknown',
                'ui.retry': 'Retry',
                'ui.download_speed': 'Speed',
                'ui.eta': 'ETA',
                'ui.connections': 'Connections',
                'ui.seeders': 'Seeders',
                'ui.category': 'Category',
                'ui.confirm_action': 'Confirm Action',
                'ui.are_you_sure': 'Are you sure?',
                'ui.cancel': 'Cancel',
                'ui.confirm': 'Confirm',
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
                'categories.other': 'Other',
                'filter.all_status': 'All Status',
                'filter.all_categories': 'All Categories',
                'messages.download_started': 'Download started',
                'messages.download_failed': 'Download failed',
                'messages.file_deleted': 'File deleted successfully',
                'messages.confirm_delete': 'Are you sure you want to delete',
                'messages.action_failed': 'Action failed',
                'messages.download_paused': 'Download paused',
                'messages.download_resumed': 'Download resumed',
                'messages.download_removed': 'Download removed',
                'messages.invalid_magnet': 'Invalid magnet link',
                'messages.no_urls_found': 'No URLs found in the text file',
                'ui.confirm_remove': 'Are you sure you want to remove this download?',
                'errors.file_not_found': 'File not found'
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
                'ui.or_upload_urls': '或上传包含URL的文本文件',
                'ui.upload_file': '上传文件',
                'ui.urls_per_line': 'URL列表（每行一个）',
                'ui.download': '下载',
                'ui.delete': '删除',
                'ui.no_downloads': '暂无下载',
                'ui.no_files': '暂无文件',
                'ui.unknown': '未知',
                'ui.retry': '重试',
                'ui.download_speed': '速度',
                'ui.eta': '剩余时间',
                'ui.connections': '连接数',
                'ui.seeders': '种子数',
                'ui.category': '分类',
                'ui.confirm_action': '确认操作',
                'ui.are_you_sure': '确定吗？',
                'ui.cancel': '取消',
                'ui.confirm': '确认',
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
                'categories.other': '其他',
                'filter.all_status': '全部状态',
                'filter.all_categories': '全部分类',
                'messages.download_started': '下载已开始',
                'messages.download_failed': '下载失败',
                'messages.file_deleted': '文件删除成功',
                'messages.confirm_delete': '确定要删除',
                'messages.action_failed': '操作失败',
                'messages.download_paused': '下载已暂停',
                'messages.download_resumed': '下载已继续',
                'messages.download_removed': '下载已删除',
                'messages.invalid_magnet': '无效的磁力链接',
                'messages.no_urls_found': '文本文件中未找到URL',
                'ui.confirm_remove': '确定要删除此下载吗？',
                'errors.file_not_found': '文件未找到'
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
                'ui.or_upload_urls': 'またはURLを含むテキストファイルをアップロード',
                'ui.upload_file': 'ファイルをアップロード',
                'ui.urls_per_line': 'URLリスト（1行に1つ）',
                'ui.download': 'ダウンロード',
                'ui.delete': '削除',
                'ui.no_downloads': 'ダウンロードなし',
                'ui.no_files': 'ファイルなし',
                'ui.unknown': '不明',
                'ui.retry': '再試行',
                'ui.download_speed': '速度',
                'ui.eta': '残り時間',
                'ui.connections': '接続数',
                'ui.seeders': 'シーダー数',
                'ui.category': 'カテゴリ',
                'ui.confirm_action': '操作の確認',
                'ui.are_you_sure': '本当によろしいですか？',
                'ui.cancel': 'キャンセル',
                'ui.confirm': '確認',
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
                'categories.other': 'その他',
                'filter.all_status': 'すべての状態',
                'filter.all_categories': 'すべてのカテゴリ',
                'messages.download_started': 'ダウンロードを開始しました',
                'messages.download_failed': 'ダウンロードに失敗しました',
                'messages.file_deleted': 'ファイルを削除しました',
                'messages.confirm_delete': '本当に削除しますか',
                'messages.action_failed': '操作に失敗しました',
                'messages.download_paused': 'ダウンロードを一時停止しました',
                'messages.download_resumed': 'ダウンロードを再開しました',
                'messages.download_removed': 'ダウンロードを削除しました',
                'messages.invalid_magnet': '無効なマグネットリンク',
                'messages.no_urls_found': 'テキストファイルにURLが見つかりません',
                'ui.confirm_remove': '本当にこのダウンロードを削除しますか？',
                'errors.file_not_found': 'ファイルが見つかりません'
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
            console.warn(`Translation not found for key: ${key}`);
            return key;
        }
        
        // Replace variables
        return this.replaceVariables(translation, variables);
    }
    
    getNestedValue(obj, key) {
        // First try direct key lookup (for flat structure)
        if (obj[key] !== undefined) {
            return obj[key];
        }
        
        // Then try nested lookup (for nested structure)
        const result = key.split('.').reduce((current, keyPart) => {
            return current && current[keyPart] !== undefined ? current[keyPart] : undefined;
        }, obj);
        
        return result !== undefined ? result : null;
    }
    
    replaceVariables(text, variables) {
        return text.replace(/\{(\w+)\}/g, (match, key) => {
            return variables[key] !== undefined ? variables[key] : match;
        });
    }
    
    applyTranslations() {
        // Translate elements with data-i18n attribute
        // Process in reverse order to handle nested elements correctly
        const elements = Array.from(document.querySelectorAll('[data-i18n]')).reverse();
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
        
        // Update custom dropdowns
        this.updateCustomDropdowns();
        
        // Update file list if it exists
        if (window.ui && window.ui.files && window.ui.files.length > 0) {
            window.ui.renderFiles();
        }
        
        // Update downloads list if it exists
        if (window.ui && window.ui.downloads && window.ui.downloads.size > 0) {
            window.ui.renderDownloads();
        }
    }
    
    updateLanguageSelector() {
        const languageSelector = document.getElementById('languageSelector');
        if (languageSelector) {
            const selectedValue = languageSelector.querySelector('.selected-value');
            if (selectedValue) {
                selectedValue.textContent = this.availableLanguages[this.currentLanguage];
            }
            
            const options = languageSelector.querySelectorAll('.custom-select-option');
            options.forEach((option) => {
                const value = option.getAttribute('data-value');
                const span = option.querySelector('span');
                if (span && this.availableLanguages[value]) {
                    span.textContent = this.availableLanguages[value];
                }
            });
        }
    }
    
    updateCustomDropdowns() {
        const updateDropdown = (dropdownId) => {
            const dropdown = document.getElementById(dropdownId);
            if (!dropdown) return;
            
            const selectedValue = dropdown.querySelector('.selected-value');
            const selectedOption = dropdown.querySelector('.custom-select-option.selected');
            
            if (selectedOption) {
                const span = selectedOption.querySelector('span');
                if (span && span.hasAttribute('data-i18n')) {
                    const translation = this.translate(span.getAttribute('data-i18n'));
                    span.textContent = translation;
                    if (selectedValue) {
                        selectedValue.textContent = translation;
                    }
                }
            }
            
            const options = dropdown.querySelectorAll('.custom-select-option:not(.selected)');
            options.forEach((option) => {
                const span = option.querySelector('span');
                if (span && span.hasAttribute('data-i18n')) {
                    span.textContent = this.translate(span.getAttribute('data-i18n'));
                }
            });
        };
        
        updateDropdown('statusFilter');
        updateDropdown('categoryFilter');
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


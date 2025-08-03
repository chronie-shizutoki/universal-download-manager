"""
Internationalization service
"""
import json
import os
from typing import Dict, Any, Optional
from ..config.settings import Config, BACKEND_DIR

class I18nService:
    """Internationalization service for multi-language support"""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.current_language = Config.DEFAULT_LANGUAGE
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files"""
        locales_dir = BACKEND_DIR / "locales"
        
        for language in Config.LANGUAGES.keys():
            locale_file = locales_dir / f"{language}.json"
            
            if locale_file.exists():
                try:
                    with open(locale_file, 'r', encoding='utf-8') as f:
                        self.translations[language] = json.load(f)
                except Exception as e:
                    print(f"Error loading translation file {locale_file}: {e}")
                    self.translations[language] = {}
            else:
                self.translations[language] = {}
    
    def set_language(self, language: str) -> bool:
        """Set current language"""
        if language in Config.LANGUAGES:
            self.current_language = language
            return True
        return False
    
    def get_language(self) -> str:
        """Get current language"""
        return self.current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages"""
        return Config.LANGUAGES
    
    def translate(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Translate a key to the specified language
        
        Args:
            key: Translation key in dot notation (e.g., 'ui.start_download')
            language: Target language (uses current language if None)
            **kwargs: Variables for string formatting
        
        Returns:
            Translated string or the key if translation not found
        """
        if language is None:
            language = self.current_language
        
        if language not in self.translations:
            language = Config.DEFAULT_LANGUAGE
        
        # Navigate through nested dictionary using dot notation
        translation = self.translations.get(language, {})
        keys = key.split('.')
        
        for k in keys:
            if isinstance(translation, dict) and k in translation:
                translation = translation[k]
            else:
                # Fallback to default language
                if language != Config.DEFAULT_LANGUAGE:
                    return self.translate(key, Config.DEFAULT_LANGUAGE, **kwargs)
                # Return key if translation not found
                return key
        
        # Format string with provided variables
        if isinstance(translation, str) and kwargs:
            try:
                return translation.format(**kwargs)
            except (KeyError, ValueError):
                return translation
        
        return str(translation)
    
    def t(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """Shorthand for translate method"""
        return self.translate(key, language, **kwargs)
    
    def get_translations(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get all translations for a language"""
        if language is None:
            language = self.current_language
        
        return self.translations.get(language, {})
    
    def get_status_text(self, status: str, language: Optional[str] = None) -> str:
        """Get localized status text"""
        return self.translate(f"status.{status}", language)
    
    def get_category_text(self, category: str, language: Optional[str] = None) -> str:
        """Get localized category text"""
        return self.translate(f"categories.{category}", language)
    
    def get_error_message(self, error_key: str, language: Optional[str] = None, **kwargs) -> str:
        """Get localized error message"""
        return self.translate(f"errors.{error_key}", language, **kwargs)
    
    def get_ui_text(self, ui_key: str, language: Optional[str] = None, **kwargs) -> str:
        """Get localized UI text"""
        return self.translate(f"ui.{ui_key}", language, **kwargs)

# Global i18n service instance
i18n = I18nService()


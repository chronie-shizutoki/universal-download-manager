/**
 * Custom Dropdown Component
 */
class CustomDropdown {
    constructor(container, options = {}) {
        this.container = container;
        this.trigger = container.querySelector('.custom-select-trigger');
        this.menu = container.querySelector('.custom-select-menu');
        this.selectedValue = container.querySelector('.selected-value');
        this.options = container.querySelectorAll('.custom-select-option');
        this.arrow = container.querySelector('.arrow');
        
        this.isOpen = false;
        this.selectedOption = null;
        
        this.onChange = options.onChange || (() => {});
        this.onOpen = options.onOpen || (() => {});
        this.onClose = options.onClose || (() => {});
        
        this.init();
    }
    
    init() {
        this.trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        this.options.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                this.selectOption(option);
            });
            
            option.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.selectOption(option);
                }
            });
        });
        
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.close();
            }
        });
        
        document.addEventListener('keydown', (e) => {
            if (this.isOpen) {
                if (e.key === 'Escape') {
                    this.close();
                    this.trigger.focus();
                } else if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    this.focusNextOption();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    this.focusPreviousOption();
                }
            }
        });
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.isOpen = true;
        this.trigger.classList.add('active');
        this.menu.classList.add('show');
        this.onOpen();
    }
    
    close() {
        this.isOpen = false;
        this.trigger.classList.remove('active');
        this.menu.classList.remove('show');
        this.onClose();
    }
    
    selectOption(option) {
        const value = option.getAttribute('data-value');
        const span = option.querySelector('span');
        const text = span ? span.textContent : '';
        
        this.options.forEach(opt => {
            opt.classList.remove('selected');
            opt.setAttribute('tabindex', '-1');
        });
        
        option.classList.add('selected');
        option.setAttribute('tabindex', '0');
        
        this.selectedValue.textContent = text;
        this.selectedOption = option;
        
        this.close();
        this.onChange(value, text);
    }
    
    getValue() {
        return this.selectedOption ? this.selectedOption.getAttribute('data-value') : null;
    }
    
    setValue(value) {
        const option = Array.from(this.options).find(opt => 
            opt.getAttribute('data-value') === value
        );
        
        if (option) {
            this.selectOption(option);
        }
    }
    
    focusNextOption() {
        const currentIndex = Array.from(this.options).findIndex(opt => 
            opt.classList.contains('selected')
        );
        const nextIndex = (currentIndex + 1) % this.options.length;
        this.options[nextIndex].focus();
    }
    
    focusPreviousOption() {
        const currentIndex = Array.from(this.options).findIndex(opt => 
            opt.classList.contains('selected')
        );
        const prevIndex = (currentIndex - 1 + this.options.length) % this.options.length;
        this.options[prevIndex].focus();
    }
    
    destroy() {
        this.trigger.removeEventListener('click');
        this.options.forEach(option => {
            option.removeEventListener('click');
            option.removeEventListener('keydown');
        });
    }
}

// Initialize all custom dropdowns
function initCustomDropdowns() {
    const dropdowns = document.querySelectorAll('.custom-select');
    
    dropdowns.forEach(container => {
        const id = container.id;
        
        if (id === 'languageSelector') {
            new CustomDropdown(container, {
                onChange: (value) => {
                    if (window.i18n) {
                        window.i18n.setLanguage(value);
                    }
                },
                onOpen: () => {
                    if (window.i18n) {
                        window.i18n.updateLanguageSelector();
                    }
                }
            });
        } else if (id === 'statusFilter') {
            new CustomDropdown(container, {
                onChange: (value) => {
                    if (window.app) {
                        window.app.filterStatus = value;
                        window.app.loadProgress();
                    }
                },
                onOpen: () => {
                    if (window.i18n) {
                        window.i18n.updateCustomDropdowns();
                    }
                }
            });
        } else if (id === 'categoryFilter') {
            new CustomDropdown(container, {
                onChange: (value) => {
                    if (window.app) {
                        window.app.filterCategory = value;
                        window.app.loadProgress();
                    }
                },
                onOpen: () => {
                    if (window.i18n) {
                        window.i18n.updateCustomDropdowns();
                    }
                }
            });
        }
    });
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCustomDropdowns);
} else {
    initCustomDropdowns();
}

// Export for manual initialization
window.CustomDropdown = CustomDropdown;
window.initCustomDropdowns = initCustomDropdowns;
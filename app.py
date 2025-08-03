"""
Universal Download Manager - Flask Application
"""
import os
import sys
from pathlib import Path

# Add backend to Python path
BACKEND_DIR = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
import logging
from datetime import datetime

# Import services
from backend.services.aria2_service import aria2_service
from backend.services.download_service import download_service
from backend.services.file_service import file_service
from backend.services.i18n_service import i18n
from backend.config.settings import Config, DOWNLOADS_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Configure app
    app.config.update(
        SECRET_KEY=Config.SECRET_KEY,
        MAX_CONTENT_LENGTH=Config.MAX_UPLOAD_SIZE,
        UPLOAD_FOLDER=str(DOWNLOADS_DIR)
    )
    
    # Initialize services on startup
    def initialize_services():
        """Initialize services on startup"""
        try:
            # Start aria2 daemon
            aria2_service.start_daemon()
            logger.info("Application initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
    
    # Call initialization immediately
    initialize_services()
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Endpoint not found',
            'error_code': 'NOT_FOUND'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 'Method not allowed',
            'error_code': 'METHOD_NOT_ALLOWED'
        }), 405
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'success': False,
            'error': 'File too large',
            'error_code': 'FILE_TOO_LARGE'
        }), 413
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'error_code': 'INTERNAL_ERROR'
        }), 500
    
    # Middleware for language detection
    @app.before_request
    def set_language():
        """Set language based on Accept-Language header"""
        if request.headers.get('Accept-Language'):
            lang = request.headers.get('Accept-Language')
            if lang in i18n.get_available_languages():
                i18n.set_language(lang)
    
    # Static files
    @app.route('/')
    def index():
        """Serve main page"""
        return send_from_directory('frontend', 'index.html')
    
    @app.route('/<path:filename>')
    def static_files(filename):
        """Serve static files"""
        return send_from_directory('frontend', filename)
    
    # API Routes
    
    # System API
    @app.route('/api/v1/system/test', methods=['GET'])
    def test_system():
        """Test system status"""
        try:
            result = aria2_service.test_connection()
            return jsonify({
                'success': True,
                **result
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'SYSTEM_TEST_FAILED'
            }), 500
    
    # Download API
    @app.route('/api/v1/downloads', methods=['GET'])
    def get_downloads():
        """Get download list"""
        try:
            status = request.args.get('status', 'all')
            category = request.args.get('category', '')
            limit = int(request.args.get('limit', 100))
            
            result = download_service.get_downloads(status, category, limit)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/downloads', methods=['POST'])
    def add_download():
        """Add new download"""
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided',
                    'error_code': 'NO_DATA'
                }), 400
            
            download_type = data.get('type', 'url')
            
            if download_type == 'url':
                url = data.get('url')
                if not url:
                    return jsonify({
                        'success': False,
                        'error': 'URL is required',
                        'error_code': 'MISSING_URL'
                    }), 400
                
                result = download_service.add_url(url, data.get('options'))
                
            elif download_type == 'magnet':
                magnet = data.get('url')
                if not magnet:
                    return jsonify({
                        'success': False,
                        'error': 'Magnet URL is required',
                        'error_code': 'MISSING_MAGNET'
                    }), 400
                
                result = download_service.add_magnet(magnet, data.get('options'))
                
            elif download_type == 'batch':
                urls = data.get('urls', [])
                if not urls:
                    return jsonify({
                        'success': False,
                        'error': 'URLs list is required',
                        'error_code': 'MISSING_URLS'
                    }), 400
                
                result = download_service.add_batch_urls(urls, data.get('options'))
                
            else:
                return jsonify({
                    'success': False,
                    'error': 'Invalid download type',
                    'error_code': 'INVALID_TYPE'
                }), 400
            
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/downloads/url', methods=['POST'])
    def add_url():
        """Add URL download"""
        try:
            data = request.get_json()
            url = data.get('url') if data else None
            
            if not url:
                return jsonify({
                    'success': False,
                    'error': 'URL is required',
                    'error_code': 'MISSING_URL'
                }), 400
            
            result = download_service.add_url(url, data.get('options'))
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/downloads/magnet', methods=['POST'])
    def add_magnet():
        """Add magnet download"""
        try:
            data = request.get_json()
            magnet = data.get('url') if data else None
            
            if not magnet:
                return jsonify({
                    'success': False,
                    'error': 'Magnet URL is required',
                    'error_code': 'MISSING_MAGNET'
                }), 400
            
            result = download_service.add_magnet(magnet, data.get('options'))
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/downloads/torrent', methods=['POST'])
    def add_torrent():
        """Add torrent file download"""
        try:
            if 'torrent' not in request.files:
                return jsonify({
                    'success': False,
                    'error': 'No torrent file provided',
                    'error_code': 'NO_FILE'
                }), 400
            
            file = request.files['torrent']
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected',
                    'error_code': 'NO_FILE'
                }), 400
            
            if not file.filename.lower().endswith('.torrent'):
                return jsonify({
                    'success': False,
                    'error': 'Invalid file type',
                    'error_code': 'INVALID_FILE_TYPE'
                }), 400
            
            file_content = file.read()
            filename = secure_filename(file.filename)
            
            result = download_service.add_torrent_file(file_content, filename)
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/downloads/batch', methods=['POST'])
    def add_batch():
        """Add batch downloads"""
        try:
            data = request.get_json()
            urls = data.get('urls', []) if data else []
            
            if not urls:
                return jsonify({
                    'success': False,
                    'error': 'URLs list is required',
                    'error_code': 'MISSING_URLS'
                }), 400
            
            result = download_service.add_batch_urls(urls, data.get('options'))
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/downloads/<gid>', methods=['GET'])
    def get_download(gid):
        """Get specific download"""
        try:
            result = download_service.get_download(gid)
            status_code = 200 if result['success'] else 404
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/downloads/<gid>/pause', methods=['POST'])
    def pause_download(gid):
        """Pause download"""
        try:
            result = download_service.pause_download(gid)
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/downloads/<gid>/resume', methods=['POST'])
    def resume_download(gid):
        """Resume download"""
        try:
            result = download_service.resume_download(gid)
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/downloads/<gid>', methods=['DELETE'])
    def remove_download(gid):
        """Remove download"""
        try:
            force = request.args.get('force', 'false').lower() == 'true'
            result = download_service.remove_download(gid, force)
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/downloads/<gid>/retry', methods=['POST'])
    def retry_download(gid):
        """Retry download"""
        try:
            result = download_service.retry_download(gid)
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    # Files API
    @app.route('/api/v1/files', methods=['GET'])
    def get_files():
        """Get files list"""
        try:
            category = request.args.get('category', '')
            sort_by = request.args.get('sort_by', 'name')
            sort_order = request.args.get('sort_order', 'asc')
            
            result = file_service.get_files(category, sort_by, sort_order)
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/files/<path:filename>/download', methods=['GET'])
    def download_file(filename):
        """Download file"""
        try:
            file_path = file_service.get_file_path(filename)
            
            if not file_path:
                return jsonify({
                    'success': False,
                    'error': 'File not found',
                    'error_code': 'FILE_NOT_FOUND'
                }), 404
            
            return send_file(
                file_path,
                as_attachment=True,
                download_name=file_path.name
            )
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/files/<path:filename>', methods=['DELETE'])
    def delete_file(filename):
        """Delete file"""
        try:
            result = file_service.delete_file(filename)
            status_code = 200 if result['success'] else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    # Statistics API
    @app.route('/api/v1/statistics', methods=['GET'])
    def get_statistics():
        """Get download statistics"""
        try:
            result = download_service.get_statistics()
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    # I18n API
    @app.route('/api/v1/i18n/<language>', methods=['GET'])
    def get_translations(language):
        """Get translations for language"""
        try:
            translations = i18n.get_translations(language)
            return jsonify(translations)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    @app.route('/api/v1/i18n/languages', methods=['GET'])
    def get_languages():
        """Get available languages"""
        try:
            languages = i18n.get_available_languages()
            return jsonify({
                'success': True,
                'languages': languages
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'error_code': 'UNKNOWN_ERROR'
            }), 500
    
    # Health check
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Universal Download Manager on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )


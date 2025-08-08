## 🌐 Language:

  - [English](README.md)
  - [日本語](README-ja.md)
  - [中文](README-zh.md)

# Universal Download Manager

A modern universal download manager that supports multiple download protocols and file types.

## 🚀 Features

### Multi-protocol Support
- **HTTP/HTTPS** - Standard web file downloads
- **FTP/FTPS** - File transfer protocol downloads
- **Magnet Links** - BitTorrent magnet link downloads
- **Torrent Files** - .torrent file downloads
- **Batch Downloads** - Support for multiple simultaneous URL downloads

### Modern Interface
- 🎨 **Responsive Design** - Perfectly adapted for desktop and mobile devices
- 🌙 **Dark/Light Themes** - Theme switching support
- 📱 **Multi-tab Interface** - Clear function categorization
- 🎯 **Drag and Drop Upload** - Support for dragging torrent files and URL lists
- ⚡ **Real-time Progress** - Animated progress bars and status updates
- 🔍 **Filter Search** - Filter downloads by status and category

### Internationalization Support
- 🌍 **Multi-language** - Support for Chinese, English, and Japanese
- 🔄 **Dynamic Switching** - Language switching at runtime
- 📝 **Complete Translation** - Full front-end and back-end internationalization

### Technical Features
- 🏗️ **Modular Architecture** - Clear code structure
- 🔧 **Configuration Management** - Flexible configuration system
- 🛡️ **Security Verification** - File and URL security checks
- 📊 **Real-time Statistics** - Download speed and progress statistics
- 🔌 **WebSocket** - Real-time status updates

<img width="1704" height="869" alt="image" src="https://github.com/user-attachments/assets/250e1a36-27f5-4e30-90a9-8bde1f4a03a2" />
<img width="1691" height="869" alt="image" src="https://github.com/user-attachments/assets/9242f25e-3849-4ba7-ae53-6d7f9500eab4" />



## 📦 Installation and Deployment

### System Requirements
- Python 3.8+
- aria2c
- Modern browser

### Quick Start

1. **Clone the Project**
```bash
git clone <repository-url>
cd magnet_refactored
```

2. **Install Dependencies**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install aria2 (Ubuntu/Debian)
sudo apt update && sudo apt install -y aria2

# Install aria2 (macOS)
brew install aria2

# Install aria2 (Windows)
# Download and install aria2 from https://aria2.github.io/
```

3. **Start the Application**
```bash
python app.py
```

4. **Access the Application**
Open your browser and visit `http://localhost:5000`

## 🏗️ Project Structure

```
magnet_refactored/
├── app.py                 # Flask main application
├── requirements.txt       # Python dependencies
├── README.md             # Project description
├── backend/              # Backend code
│   ├── config/          # Configuration management
│   │   ├── settings.py  # Application configuration
│   │   └── aria2.py     # aria2 configuration
│   ├── models/          # Data models
│   │   └── download.py  # Download task model
│   ├── services/        # Business services
│   │   ├── aria2_service.py    # aria2 service
│   │   ├── download_service.py # Download service
│   │   ├── file_service.py     # File service
│   │   └── i18n_service.py     # Internationalization service
│   ├── utils/           # Utility functions
│   │   ├── validators.py # Validation tools
│   │   └── formatters.py # Formatting tools
│   └── locales/         # Internationalization files
│       ├── en.json      # English translation
│       ├── zh.json      # Chinese translation
│       └── ja.json      # Japanese translation
├── frontend/            # Frontend code
│   ├── index.html       # Main page
│   ├── css/            # Style files
│   │   ├── main.css    # Main styles
│   │   └── themes.css  # Theme styles
│   └── js/             # JavaScript files
│       ├── app.js      # Main application logic
│       ├── ui.js       # UI interaction logic
│       ├── api.js      # API call wrapper
│       └── i18n.js     # Frontend internationalization
└── downloads/          # Download files directory
```

## 🔧 Configuration Instructions

### Environment Variables
```bash
# Flask configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# aria2 configuration
ARIA2_RPC_PORT=6800
ARIA2_RPC_SECRET=your_secret

# Download configuration
MAX_CONNECTIONS_PER_SERVER=4
MAX_RETRIES=3
DOWNLOAD_TIMEOUT=60

# BitTorrent configuration
BT_MAX_PEERS=50
SEED_RATIO=1.0
SEED_TIME=60
```

### aria2 Configuration
The application automatically starts and manages the aria2c daemon with the following features:
- Automatic reconnection and error recovery
- Session saving and restoration
- Multi-connection download optimization
- BitTorrent protocol support

## 📚 API Documentation

### Download Management
- `GET /api/v1/downloads` - Get download list
- `POST /api/v1/downloads/url` - Add URL download
- `POST /api/v1/downloads/magnet` - Add magnet link
- `POST /api/v1/downloads/torrent` - Upload torrent file
- `POST /api/v1/downloads/batch` - Add batch downloads
- `POST /api/v1/downloads/{gid}/pause` - Pause download
- `POST /api/v1/downloads/{gid}/resume` - Resume download
- `DELETE /api/v1/downloads/{gid}` - Delete download

### File Management
- `GET /api/v1/files` - Get file list
- `GET /api/v1/files/{filename}/download` - Download file
- `DELETE /api/v1/files/{filename}` - Delete file

### System Status
- `GET /api/v1/system/test` - Test system status
- `GET /api/v1/statistics` - Get download statistics
- `GET /api/v1/health` - Health check

## 🤝 Contribution Guide

Welcome to submit Issues and Pull Requests!

## 📄 License

MIT License

## 🔗 Related Links

- [aria2 Official Website](https://aria2.github.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)

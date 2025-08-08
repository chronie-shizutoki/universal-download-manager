# Universal Download Manager

一个现代化的通用下载管理器，支持多种下载协议和文件类型。

## 🚀 功能特性

### 多协议支持
- **HTTP/HTTPS** - 标准网页文件下载
- **FTP/FTPS** - 文件传输协议下载
- **磁力链接** - BitTorrent 磁力链接下载
- **种子文件** - .torrent 文件下载
- **批量下载** - 支持多个URL同时下载

### 现代化界面
- 🎨 **响应式设计** - 完美适配桌面和移动设备
- 🌙 **深色/浅色主题** - 支持主题切换
- 📱 **多标签页界面** - 清晰的功能分类
- 🎯 **拖拽上传** - 支持拖拽种子文件和URL列表
- ⚡ **实时进度** - 动画进度条和状态更新
- 🔍 **过滤搜索** - 按状态和类别过滤下载

### 国际化支持
- 🌍 **多语言** - 支持中文、英文、日文
- 🔄 **动态切换** - 运行时切换语言
- 📝 **完整翻译** - 前后端完整国际化

### 技术特性
- 🏗️ **模块化架构** - 清晰的代码结构
- 🔧 **配置管理** - 灵活的配置系统
- 🛡️ **安全验证** - 文件和URL安全检查
- 📊 **实时统计** - 下载速度和进度统计
- 🔌 **WebSocket** - 实时状态更新

## 📦 安装部署

### 系统要求
- Python 3.8+
- aria2c
- 现代浏览器

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd magnet_refactored
```

2. **安装依赖**
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 aria2 (Ubuntu/Debian)
sudo apt update && sudo apt install -y aria2

# 安装 aria2 (macOS)
brew install aria2

# 安装 aria2 (Windows)
# 下载并安装 aria2 from https://aria2.github.io/
```

3. **启动应用**
```bash
python app.py
```

4. **访问应用**
打开浏览器访问 `http://localhost:5000`

## 🏗️ 项目结构

```
magnet_refactored/
├── app.py                 # Flask 主应用
├── requirements.txt       # Python 依赖
├── README.md             # 项目说明
├── backend/              # 后端代码
│   ├── config/          # 配置管理
│   │   ├── settings.py  # 应用配置
│   │   └── aria2.py     # aria2 配置
│   ├── models/          # 数据模型
│   │   └── download.py  # 下载任务模型
│   ├── services/        # 业务服务
│   │   ├── aria2_service.py    # aria2 服务
│   │   ├── download_service.py # 下载服务
│   │   ├── file_service.py     # 文件服务
│   │   └── i18n_service.py     # 国际化服务
│   ├── utils/           # 工具函数
│   │   ├── validators.py # 验证工具
│   │   └── formatters.py # 格式化工具
│   └── locales/         # 国际化文件
│       ├── en.json      # 英文翻译
│       ├── zh.json      # 中文翻译
│       └── ja.json      # 日文翻译
├── frontend/            # 前端代码
│   ├── index.html       # 主页面
│   ├── css/            # 样式文件
│   │   ├── main.css    # 主样式
│   │   └── themes.css  # 主题样式
│   └── js/             # JavaScript 文件
│       ├── app.js      # 主应用逻辑
│       ├── ui.js       # UI 交互逻辑
│       ├── api.js      # API 调用封装
│       └── i18n.js     # 前端国际化
└── downloads/          # 下载文件目录
```

## 🔧 配置说明

### 环境变量
```bash
# Flask 配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# aria2 配置
ARIA2_RPC_PORT=6800
ARIA2_RPC_SECRET=your_secret

# 下载配置
MAX_CONNECTIONS_PER_SERVER=4
MAX_RETRIES=3
DOWNLOAD_TIMEOUT=60

# BitTorrent 配置
BT_MAX_PEERS=50
SEED_RATIO=1.0
SEED_TIME=60
```

### aria2 配置
应用会自动启动和管理 aria2c 守护进程，支持以下功能：
- 自动重连和错误恢复
- 会话保存和恢复
- 多连接下载优化
- BitTorrent 协议支持

## 📚 API 文档

### 下载管理
- `GET /api/v1/downloads` - 获取下载列表
- `POST /api/v1/downloads/url` - 添加URL下载
- `POST /api/v1/downloads/magnet` - 添加磁力链接
- `POST /api/v1/downloads/torrent` - 上传种子文件
- `POST /api/v1/downloads/batch` - 批量添加下载
- `POST /api/v1/downloads/{gid}/pause` - 暂停下载
- `POST /api/v1/downloads/{gid}/resume` - 恢复下载
- `DELETE /api/v1/downloads/{gid}` - 删除下载

### 文件管理
- `GET /api/v1/files` - 获取文件列表
- `GET /api/v1/files/{filename}/download` - 下载文件
- `DELETE /api/v1/files/{filename}` - 删除文件

### 系统状态
- `GET /api/v1/system/test` - 测试系统状态
- `GET /api/v1/statistics` - 获取下载统计
- `GET /api/v1/health` - 健康检查

## 🌟 主要改进

### 相比原项目的改进
1. **解决高耦合问题**
   - 前后端完全分离
   - 模块化架构设计
   - 清晰的服务层划分

2. **解决中文硬编码问题**
   - 完整的国际化支持
   - 多语言动态切换
   - 前后端统一翻译

3. **界面设计优化**
   - 现代化响应式设计
   - 深色/浅色主题支持
   - 更好的用户体验

4. **功能扩展**
   - 支持更多下载协议
   - 批量下载功能
   - 文件管理界面
   - 实时进度更新

5. **代码质量提升**
   - 完整的错误处理
   - 安全性验证
   - 配置管理优化
   - 代码文档完善

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [aria2 官网](https://aria2.github.io/)
- [Flask 文档](https://flask.palletsprojects.com/)


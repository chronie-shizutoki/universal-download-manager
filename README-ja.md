## 🌐 言語:

  - [日本語](README-ja.md)
  - [English](README.md)
  - [中文](README-zh.md)

# ユニバーサルダウンロードマネージャー

最新の汎用ダウンロードマネージャーで、さまざまなダウンロードプロトコルとファイル形式に対応しています。

## 🚀 機能特性

### 多プロトコル対応
- **HTTP/HTTPS** - 標準的なウェブページのファイルダウンロード
- **FTP/FTPS** - ファイル転送プロトコルによるダウンロード
- **磁力リンク** - BitTorrent 磁力リンクのダウンロード
- **トレントファイル** - .torrent ファイルのダウンロード
- **一括ダウンロード** - 複数のURLを同時にダウンロードできます

### 最新のインターフェース
- 🎨 **レスポンシブデザイン** - デスクトップとモバイルデバイスに完全に適合します
- 🌙 **ダーク/ライトテーマ** - テーマを切り替えることができます
- 📱 **多タブインターフェース** - 機能を明確に分類します
- 🎯 **ドラッグアンドドロップ** - トレントファイルとURLリストのドラッグアンドドロップに対応しています
- ⚡ **リアルタイム進捗** - アニメーション付きの進捗バーとステータス更新
- 🔍 **フィルター検索** - ステータスとカテゴリーでダウンロードをフィルタリングできます

### 国際化対応
- 🌍 **多言語** - 中国語、英語、日本語に対応しています
- 🔄 **動的切り替え** - 実行時に言語を切り替えることができます
- 📝 **完全翻訳** - フロントエンドとバックエンドの完全な国際化

### 技術的特長
- 🏗️ **モジュール化アーキテクチャ** - 明確なコード構造
- 🔧 **設定管理** - 柔軟な設定システム
- 🛡️ **セキュリティ検証** - ファイルとURLのセキュリティチェック
- 📊 **リアルタイム統計** - ダウンロード速度と進捗状況の統計
- 🔌 **WebSocket** - リアルタイムステータス更新

## 📦 インストールとデプロイ

### システム要件
- Python 3.8 以上
- aria2c
- 最新のブラウザ

### クイックスタート

1. **プロジェクトをクローンする**
```bash
git clone <repository-url>
cd magnet_refactored
```

2. **依存関係のインストール**
```bash
# Python 依存関係のインストール
pip install -r requirements.txt

# aria2 のインストール (Ubuntu/Debian)
sudo apt update && sudo apt install -y aria2

# aria2 のインストール (macOS)
brew install aria2

# aria2 のインストール (Windows)
# https://aria2.github.io/ から aria2 をダウンロードしてインストールします
```

3. **アプリケーションを起動する**
```bash
python app.py
```

4. **アプリケーションにアクセスする**
ブラウザを開き、`http://localhost:5000` にアクセスします。

## 🏗️ プロジェクト構造

```
magnet_refactored/
├── app.py                 # Flask 主アプリケーション
├── requirements.txt       # Python 依存関係
├── README.md             # プロジェクト説明
├── backend/              # バックエンドコード
│   ├── config/          # 設定管理
│   │   ├── settings.py  # アプリケーション設定
│   │   └── aria2.py     # aria2 設定
│   ├── models/          # データモデル
│   │   └── download.py  # ダウンロードタスクモデル
│   ├── services/        # サービス
│   │   ├── aria2_service.py    # aria2 サービス
│   │   ├── download_service.py # ダウンロードサービス
│   │   ├── file_service.py     # ファイルサービス
│   │   └── i18n_service.py     # 国際化サービス
│   ├── utils/           # ユーティリティ関数
│   │   ├── validators.py # 検証ツール
│   │   └── formatters.py # フォーマッター
│   └── locales/         # 国際化ファイル
│       ├── en.json      # 英語翻訳
│       ├── zh.json      # 中国語翻訳
│       └── ja.json      # 日本語翻訳
├── frontend/            # フロントエンドコード
│   ├── index.html       # メインページ
│   ├── css/            # スタイルファイル
│   │   ├── main.css    # メインスタイル
│   │   └── themes.css  # テーマスタイル
│   └── js/             # JavaScript ファイル
│       ├── app.js      # メインアプリケーションロジック
│       ├── ui.js       # UI 交互ロジック
│       ├── api.js      # API 呼び出し封装
│       └── i18n.js     # フロントエンド国際化
└── downloads/          # ダウンロードファイルディレクトリ
```

## 🔧 設定説明

### 環境変数
```bash
# Flask 設定
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false

# aria2 設定
ARIA2_RPC_PORT=6800
ARIA2_RPC_SECRET=your_secret

# ダウンロード設定
MAX_CONNECTIONS_PER_SERVER=4
MAX_RETRIES=3
DOWNLOAD_TIMEOUT=60

# BitTorrent 設定
BT_MAX_PEERS=50
SEED_RATIO=1.0
SEED_TIME=60
```

### aria2 設定
アプリケーションは自動的に aria2c デーモンプロセスを起動し、管理します。以下の機能をサポートしています：
- 自動再接続とエラー復旧
- セッションの保存と復元
- 多接続ダウンロードの最適化
- BitTorrent プロトコルのサポート

## 📚 API ドキュメント

### ダウンロード管理
- `GET /api/v1/downloads` - ダウンロードリストを取得
- `POST /api/v1/downloads/url` - URLを追加
- `POST /api/v1/downloads/magnet` - 磁力リンクを追加
- `POST /api/v1/downloads/torrent` - トレントファイルをアップロード
- `POST /api/v1/downloads/batch` - バッチ追加
- `POST /api/v1/downloads/{gid}/pause` - ダウンロードを一時停止
- `POST /api/v1/downloads/{gid}/resume` - ダウンロードを再開
- `DELETE /api/v1/downloads/{gid}` - ダウンロードを削除

### ファイル管理
- `GET /api/v1/files` - ファイルリストを取得
- `GET /api/v1/files/{filename}/download` - ファイルをダウンロード
- `DELETE /api/v1/files/{filename}` - ファイルを削除

### システム状態
- `GET /api/v1/system/test` - システム状態をテスト
- `GET /api/v1/statistics` - ダウンロード統計を取得
- `GET /api/v1/health` - ヘルスチェック

## 🤝 貢献ガイド

Issue と Pull Request を提出してください！

## 📄 ライセンス

MIT License

## 🔗 関連リンク

- [aria2 公式ウェブサイト](https://aria2.github.io/)
- [Flask ドキュメント](https://flask.palletsprojects.com/)


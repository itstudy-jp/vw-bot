---
inclusion: always
---

# 開発ワークフローとデプロイメント

## 開発環境セットアップ

### ローカル開発
```bash
# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .env ファイルを編集して適切な値を設定
```

### Docker開発
```bash
# 開発環境での実行
make run-dev

# ログの確認
docker logs -f vw-bot

# コンテナの停止
make stop
```

## ビルドとデプロイ

### Makefileコマンド
- `make run-dev`: 開発環境でビルド・実行
- `make run-prod`: 本番環境でビルド・実行
- `make down`: コンテナ・イメージ削除
- `make stop`: コンテナ停止
- `make start`: コンテナ開始

### 環境ファイル管理
- `.env.dev`: 開発環境用設定
- `.env.prod`: 本番環境用設定
- `ENV_FILE` 環境変数で切り替え

## テストとデバッグ

### ログレベル設定
- **DEBUG**: 詳細なデバッグ情報
- **INFO**: 一般的な動作情報
- **WARNING**: 警告（時刻差異など）
- **ERROR**: エラー情報
- **CRITICAL**: 致命的エラー

### デバッグポイント
- NTP時刻同期の確認
- Discord接続状態の監視
- スケジュールタスクの実行状況
- 音声ファイルの再生確認

## 本番運用

### 監視項目
- Botのオンライン状態
- スケジュールタスクの実行
- メモリ・CPU使用率
- ログエラーの監視

### トラブルシューティング
- Discord API制限への対応
- 音声再生エラーの対処
- 時刻同期問題の解決
- 環境変数設定の確認
# CLAUDE.md

このファイルは Claude Code (claude.ai/code)がこのリポジトリでコードを扱う際のガイダンスを提供します。

**重要**: Claude Code は常に日本語で回答すること。
**重要**: .kiro/steering も見ること

## プロジェクト概要

`vw-bot`は、日本の職場向けに自動化された勤務スケジュール通知とボイスチャンネル管理を提供する Python 製の Discord ボットです。指定された時刻に Discord ボイスチャンネルに参加し、音声ファイルを再生し、日次の勤務スケジュール（JST 9:00-18:00、12:00 昼休み）に従ってメッセージを送信します。

## 開発コマンド

### Docker 開発環境

```bash
# 開発環境
make run-dev

# 本番環境
make run-prod

# コンテナ開始
make start

# コンテナ停止
make stop

# コンテナ・イメージ・ボリュームを停止・削除
make down
```

### 直接 Python 実行

```bash
# 依存関係インストール
pip install -r requirements.txt

# ボット実行（Discord認証情報が記載された.envファイルが必要）
cd src && python main.py
```

## アーキテクチャ

### コアコンポーネント

- **`main.py`**: Discord クライアントの初期化、NTP 時刻同期、スケジュールタスク登録を行うエントリーポイント
- **`utils/actions.py`**: Discord 操作（ボイスチャンネル参加/退出、音声再生、メッセージ送信）を処理する`Bot`クラス
- **`utils/async_scheduler.py`**: `ScheduleTask`クラスと NTP 時刻同期を含むカスタム非同期スケジューリングシステム
- **`utils/schedule_trigger.py`**: 勤務日のすべてのスケジュールジョブ（出退勤、時報、休憩リマインダー）を登録
- **`utils/jobs.py`**: スケジューラによって実行されるジョブ関数（勤務通知、休憩通知、ボイスチャンネル管理）
- **`utils/messages.py`**: メッセージ定数と音声ファイルマッピング
- **`utils/ntp_client.py`**: 時刻同期用 NTP クライアント

### 音声システム

ボットは FFmpeg を使用して`src/audio/`ディレクトリから音声ファイルを再生します。音声ファイルは異なる勤務イベント（出勤、開始、昼食など）に対応しています。

### 時刻管理

- 正確な時刻同期のため NTP サーバー（pool.ntp.org）を使用
- JST（Asia/Tokyo）タイムゾーンで動作
- 起動時に NTP とローカル時刻の時刻ドリフトを検証
- 平日のみ動作（月曜日〜金曜日）

### スケジュールシステム

ボットは固定スケジュールで動作：

- 8:00: ボイスチャンネル参加
- 9:00: 出勤通知
- 5 分前警告付きの時間単位勤務/休憩サイクル
- 12:00: 昼休み
- 18:00: 退勤とボイスチャンネル退出

## 環境設定

`.env.example`を基に`.env.dev`または`.env.prod`ファイルを作成：

```
DISCORD_TOKEN=your_discord_bot_token
GUILD_ID=your_discord_server_id
VOICE_CHANNEL_ID=your_voice_channel_id
```

## 主要技術詳細

- 音声サポート付き`discord.py` 2.5.2 を使用（FFmpeg が必要）
- 正確なタイミングのため`discord.utils.sleep_until()`を使用するカスタム非同期スケジューラ
- ドリフト問題を防ぐための NTP 時刻同期
- キーボード割り込みサポート付きの優雅なエラーハンドリング
- Python 3.13.3-slim ベースイメージでの Docker コンテナ化

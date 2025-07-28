---
inclusion: always
---

# Discord VC通知Bot - プロジェクト概要

このプロジェクトは、指定した時間にDiscordのボイスチャンネルに自動参加し、音声とテキストで通知を行うPython製のBotです。

## プロジェクト構造

```
├── src/
│   ├── main.py              # メインエントリーポイント
│   ├── utils/               # ユーティリティモジュール
│   │   ├── actions.py       # Bot動作クラス
│   │   ├── async_scheduler.py # 非同期スケジューラ
│   │   ├── jobs.py          # ジョブ定義
│   │   ├── messages.py      # メッセージ管理
│   │   ├── ntp_client.py    # NTP時刻同期
│   │   └── schedule_trigger.py # スケジュール登録
│   └── audio/               # 音声ファイル
├── docker-compose.yml       # Docker構成
├── Dockerfile              # Dockerイメージ定義
├── requirements.txt        # Python依存関係
└── Makefile               # ビルド・実行コマンド
```

## 主要機能

- **始業通知**: 9:00にVC参加し「おはようございます」
- **毎時通知**: 毎時00分に時刻通知
- **5分前通知**: 休憩5分前の作業終了通知
- **50分通知**: 毎時50分の休憩通知
- **昼休み通知**: 12:00の昼休み通知
- **終業通知**: 終業時の退勤通知とVC退出

## 技術スタック

- **Python 3.13**: メイン言語
- **discord.py 2.5.2**: Discord API ライブラリ
- **Docker**: コンテナ化
- **ffmpeg**: 音声処理
- **NTP**: 時刻同期

## 環境変数

- `DISCORD_TOKEN`: BotのDiscordトークン
- `GUILD_ID`: 対象サーバーID
- `VOICE_CHANNEL_ID`: 通知用VCのチャンネルID
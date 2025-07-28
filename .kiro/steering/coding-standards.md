---
inclusion: always
---

# コーディング規約とベストプラクティス

## Python コーディングスタイル

### 基本規約
- **PEP 8** に準拠したコーディングスタイルを使用
- **日本語コメント** を積極的に使用（プロジェクトの性質上）
- **型ヒント** を可能な限り使用する
- **docstring** は日本語で記述

### ファイル構造
```python
# -*- coding: utf-8 -*-
"""
モジュールの説明（日本語）
"""
# 標準ライブラリ
import os
import sys

# サードパーティライブラリ
import discord
from discord.ext import tasks

# ローカルモジュール
from utils.actions import Bot
```

### 命名規則
- **クラス名**: PascalCase (`Bot`, `NTPRetrieve`)
- **関数・変数名**: snake_case (`get_locale_time`, `discord_token`)
- **定数**: UPPER_SNAKE_CASE (`DISCORD_TOKEN`, `JOIN_TIME`)
- **プライベート**: アンダースコア接頭辞 (`_private_method`)

### エラーハンドリング
- 具体的な例外クラスをキャッチ
- ログ出力は日本語メッセージを使用
- 適切なログレベルを設定（DEBUG, INFO, WARNING, ERROR, CRITICAL）

### 非同期処理
- `async/await` を適切に使用
- Discord.py の非同期パターンに従う
- タスクの開始・停止を適切に管理

## Discord Bot 開発規約

### 権限管理
- 必要最小限の権限のみを要求
- `intents` を明示的に設定
- 権限不足時の適切なエラーハンドリング

### 時刻管理
- NTP サーバーとの時刻同期を重視
- タイムゾーン（JST）を明示的に処理
- 時刻差異の警告とユーザー確認

### 環境変数
- `.env` ファイルによる設定管理
- 本番・開発環境の分離
- 必須環境変数の検証
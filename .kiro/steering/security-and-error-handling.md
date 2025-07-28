---
inclusion: always
---

# セキュリティとエラーハンドリング

## セキュリティベストプラクティス

### 認証情報管理
```python
# 環境変数による機密情報の管理
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    logger.critical("DISCORD_TOKEN が設定されていません")
    sys.exit(1)

# .env ファイルの .gitignore 登録必須
# .env.example でテンプレート提供
```

### Discord Bot 権限
```python
# 必要最小限の権限設定
intents = discord.Intents.default()
# intents.guilds = True      # 必要な場合のみ有効化
# intents.voice_states = True # 必要な場合のみ有効化

# 権限チェックの実装
async def check_permissions(guild, channel):
    bot_member = guild.me
    permissions = channel.permissions_for(bot_member)
    
    if not permissions.connect:
        raise PermissionError("ボイスチャンネルへの接続権限がありません")
    if not permissions.speak:
        raise PermissionError("ボイスチャンネルでの発言権限がありません")
```

### 入力検証
```python
# 環境変数の型チェック
try:
    GUILD_ID: int = int(os.getenv("GUILD_ID"))
    VC_CHANNEL_ID: int = int(os.getenv("VOICE_CHANNEL_ID"))
except (TypeError, ValueError) as e:
    logger.critical(f"環境変数の形式が正しくありません: {e}")
    sys.exit(1)
```

## エラーハンドリング戦略

### 例外の階層化
```python
class BotError(Exception):
    """Bot関連の基底例外クラス"""
    pass

class ScheduleTaskError(BotError):
    """スケジュールタスク関連のエラー"""
    pass

class DiscordConnectionError(BotError):
    """Discord接続関連のエラー"""
    pass
```

### 適切なログ出力
```python
# レベル別ログ出力
logger.debug("デバッグ情報: 詳細な実行状況")
logger.info("情報: 正常な動作状況")
logger.warning("警告: 注意が必要な状況")
logger.error("エラー: 処理に失敗")
logger.critical("致命的: アプリケーション停止")

# 例外情報の詳細出力
try:
    # 処理
    pass
except Exception:
    logger.exception("予期しないエラーが発生しました")
```

### 復旧可能エラーの処理
```python
# Discord接続エラーの自動復旧
@client.event
async def on_disconnect():
    logger.warning("Discordから切断されました。再接続を試行します。")
    # 自動再接続はdiscord.pyが処理

# NTP時刻同期エラーの処理
try:
    ntp_time = ntp_retrieve.get_locale_time()
except Exception as e:
    logger.error(f"NTP時刻取得に失敗: {e}")
    logger.info("ローカル時刻を使用して続行します")
    ntp_time = datetime.now(ntp_retrieve.time_zone)
```

## 運用時の監視

### ヘルスチェック
```python
# Dockerヘルスチェックの実装
def health_check():
    """アプリケーションの健全性チェック"""
    if not client.is_ready():
        return False
    # その他のチェック項目
    return True
```

### ログ監視
- エラーレベルのログ監視
- 異常な接続切断の検出
- スケジュールタスクの実行失敗監視
- メモリ・CPU使用率の監視

### アラート設定
- 致命的エラー発生時の通知
- 長時間の接続切断検出
- リソース使用率の閾値超過
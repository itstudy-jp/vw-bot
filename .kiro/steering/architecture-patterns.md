---
inclusion: always
---

# アーキテクチャパターンと設計原則

## プロジェクト構造パターン

### モジュール分離
```
src/
├── main.py                 # エントリーポイント（初期化・イベントループ）
├── utils/
│   ├── actions.py         # Bot動作の抽象化
│   ├── async_scheduler.py # スケジューリング機能
│   ├── jobs.py           # 具体的なジョブ定義
│   ├── messages.py       # メッセージ管理
│   ├── ntp_client.py     # 外部サービス連携
│   └── schedule_trigger.py # スケジュール登録
└── audio/                 # 静的リソース
```

### 責任分離の原則
- **main.py**: アプリケーションライフサイクル管理
- **actions.py**: Discord Bot の具体的な動作
- **async_scheduler.py**: 非同期タスクスケジューリング
- **jobs.py**: ビジネスロジック（通知内容・タイミング）
- **ntp_client.py**: 外部依存の抽象化

## 設計パターン

### 非同期処理パターン
```python
# Discord.py のイベントループと協調
@tasks.loop(seconds=60)
async def discord_event_loop():
    # 定期実行処理
    pass

# 適切な例外処理
try:
    task_instance.start()
    logger.debug(f"'{task_name}' を開始しました。")
except ScheduleTaskError as e:
    logger.error(f"'{task_name}' の開始に失敗しました。 {e}")
```

### 設定管理パターン
```python
# 環境変数による設定の外部化
DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN")
GUILD_ID: int = int(os.getenv("GUILD_ID"))
VC_CHANNEL_ID: int = int(os.getenv("VOICE_CHANNEL_ID"))

# 定数の明示的定義
JOIN_TIME = dt_time(8, 0, 0, 0)
START_TIME = dt_time(9, 0, 0, 0)
END_TIME = dt_time(18, 0, 0, 0)
```

## 拡張性の考慮

### 将来の機能拡張
- スケジュールのYAML外部定義
- Web UIからの手動制御
- 複数サーバー対応
- カスタム通知メッセージ

### モジュール間の疎結合
- インターフェースによる抽象化
- 依存性注入パターンの活用
- 設定の外部化による柔軟性

## パフォーマンス考慮

### リソース管理
- Discord接続の適切な管理
- 音声ファイルのメモリ効率
- ログローテーションの実装

### スケーラビリティ
- 単一責任の原則
- 状態管理の最小化
- 外部依存の抽象化
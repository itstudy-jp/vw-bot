# Discord VC通知Bot

このプロジェクトは、指定した時間に Discord のボイスチャンネルに自動参加し、音声とテキストで通知を行う Python 製の Bot です。

## 概要

* **始業通知**：9:00 に VC に入り「おはようございます。本日も頑張りましょう。」を通知
* **毎時通知**：毎時00分に「X時になりました。開始してください。」を通知
* **5分前通知**：休憩5分前に「作業終了まで残り5分です。」を通知
* **50分通知**：毎時50分に「お疲れ様です。50分になりました。」を通知（※11時・終業前を除く）
* **昼休み通知**：12:00 に「お疲れ様です。お昼になりました。」を通知
* **終業通知**：終業時 に「本日もお疲れ様でした。」を通知し、VCを退出
* 通知はテキストチャットと音声（.wav ファイル）で実施

## セットアップ手順（Makefile + Docker / Podman）

### 1. 環境準備

#### ◾ Ubuntu（Dockerを使用）

```bash
sudo apt update
sudo apt install -y docker.io make
sudo systemctl enable --now docker

# （任意）Dockerをrootlessで使う
sudo usermod -aG docker $USER
newgrp docker
```

#### ◾ RHEL / Rocky Linux（Podman互換モードでDockerコマンドを使用）

```bash
sudo dnf install -y podman podman-docker make
```

> `podman-docker` をインストールすることで、`docker` コマンドが Podman にラップされ、Makefile をそのまま使用できます。

### 2. `.env` ファイルの作成

`.env.example` をコピーして `.env.dev`（検証環境用）または `.env.prod`（本番用）を作成し、以下のように記入してください：

```
DISCORD_TOKEN=Botのトークン
GUILD_ID=サーバーID
VC_CHANNEL_ID=通知用VCのチャンネルID
```

### 3. Bot イメージのビルドと実行

```bash
make run-dev    # イメージをdevでビルドしてコンテナ起動
make run-prod   # イメージをprodでビルドしてコンテナ起動
make down       # BOTを停止してコンテナ・イメージ削除
make stop       # BOTコンテナを停止
make start      # BOTコンテナを開始
```

### 4. ログの確認

```bash
docker logs -f vc-bot
```

> ※RHELでは `docker` は Podman によってラップされており、同様に動作します。

## 注意事項

* 音声通知には `ffmpeg` と `pynacl` ライブラリが必要です（Dockerfile 内で対応済み）
* Discord Bot には VC参加・発言・メッセージ投稿のパーミッションが必要です
* 時刻判定はシステムクロックに依存するため、タイムゾーンを確認してください（例：JST）

## 今後の展望

* スケジュールのYAML化による外部定義対応
* Web UIからの手動通知やスケジュール制御
* サービス化（systemd対応）

---

ご不明な点や改善案があれば、Issue や Pull Request にてお知らせください。

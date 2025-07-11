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

## セットアップ手順

### 1. 仮想環境の作成（共通）

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 必要ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 3. .envの作成と定数の変更

`.env.example` をコピーして `.env` を作成し、以下の情報を記入：

```
DISCORD_TOKEN=Botのトークン
GUILD_ID=サーバーID
VC_CHANNEL_ID=通知用VCのチャンネルID
```

### 4. ffmpegのインストール

#### ◾ Ubuntu 24.04

```bash
sudo apt update
sudo apt install -y ffmpeg
```

#### ◾ RHEL / Rocky Linux 9

```bash
sudo dnf install -y epel-release
sudo dnf install -y ffmpeg ffmpeg-devel
```

※ `epel-release` が見つからない場合は、EPEL RPM を [Fedora公式サイト](https://dl.fedoraproject.org/pub/epel/) からダウンロードしてインストールしてください。

### 5. Botの実行

```bash
source .venv/bin/activate
python main.py
```

## 注意事項

* 音声通知には `ffmpeg` と `pynacl` ライブラリが必要です。
* Botには VC参加・発言・メッセージ投稿のパーミッションが必要です。
* 時刻判定はシステムクロックに依存するため、タイムゾーンが正しいか確認してください（例：JST）。

## 今後の展望

* スケジュールのYAML化による外部定義対応
* Web UIからの手動通知やスケジュール制御
* サービス化（systemd対応）

---

ご不明な点や改善案があれば、Issue や Pull Request にてお知らせください。

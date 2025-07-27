# -*- coding: utf-8 -*-
"""
プログラムの起動及び初期化とDiscordイベントによるコルーチンを規定
"""
from datetime import datetime, timedelta, time as dt_time
import logging
import os
import sys

import discord
from discord.ext import tasks
from dotenv import load_dotenv

from utils.actions import Bot
from utils.async_scheduler import ScheduleTaskError
from utils.schedule_trigger import register_jobs
from utils.ntp_client import NTPRetrieve

# ===== logging =====
# TODO logging設定の外部化を検討
# TODO 外部ライブラリの規定を検討(現在はrootロガー及びライブラリ自身のハンドラを利用中)
# schedule https://schedule.readthedocs.io/en/stable/logging.html
# discord.py https://discordpy.readthedocs.io/ja/stable/logging.html
# TODO logローテートの規定を検討
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
         logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# TODO async_scheduleを完全にNTPによって動作させられるまで暫定で残す
# ===== time adjustment =====
ntp_retrieve = NTPRetrieve()
ntp_time = ntp_retrieve.get_locale_time()
local_time = datetime.now(ntp_retrieve.time_zone)
logger.info(f"NTP: {ntp_time} LOCAL: {local_time}")
time_diff = abs(ntp_time - local_time)
if time_diff >= timedelta(minutes=1):
    logger.warning(f"警告: {ntp_retrieve.ntp_host}で取得された時刻とローカル時刻の差が1分以上あります！差分: {time_diff}")
    # ユーザーに続行を促す
    while True:
        user_input = input("このまま続行しますか？ (y/n): ").lower().strip()
        if user_input == "y":
            logger.info("vw-botの起動処理を続行します。")
            break
        elif user_input == "n":
            logger.info("vw-botを終了します。")
            sys.exit(0)
        else:
            logger.info("無効な入力です。「y」または「n」を入力してください。")

# ===== environment =====
# .envの記述を環境変数へ登録
load_dotenv()

# containerで設定した環境変数は自動的に読み込まれるのでloadは不要です
# 意図が不明だったのでコードはコメントアウトで残しておきます
# 特別な理由により必要とされている場合は単体実行との共通化をどうするか考えるべきです
# env_file = os.getenv("ENV_FILE", ".env.dev")
# logger.info(f"loading env from: {env_file}")
# load_dotenv(dotenv_path=env_file)
# if "prod" in env_file:
#     ENV = "prod"
# else:
#     ENV = "dev"
#
# logger.debug(f"環境変数ファイル:{env_file} 環境:{ENV}")

DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN")
GUILD_ID: int = int(os.getenv("GUILD_ID"))
# TODO チャンネル名から探索自動化検討
VC_CHANNEL_ID: int = int(os.getenv("VOICE_CHANNEL_ID"))

# ===== schedule list =====
# TODO 定数を外部化
# 接続時刻
JOIN_TIME = dt_time(8, 0, 0, 0)
# 開始時刻
START_TIME = dt_time(9, 0, 0, 0)
# 終了時刻
END_TIME = dt_time(18, 0, 0, 0)

# ===== permission =====
# TODO 必要な権限を精査
intents = discord.Intents.default()
# intents.guilds = True
# intents.voice_states = True

# ===== client =====
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    """
    botがDiscordにログインしたとき
    """

    # botの動作を規定したクライアントを初期化
    bot = Bot(client, GUILD_ID, VC_CHANNEL_ID)

    # スケジュールを登録
    tasks_object = register_jobs(bot, JOIN_TIME, START_TIME, END_TIME)

    for task_name, task_instance in tasks_object.items():
        try:
            task_instance.start()
            logger.debug(f"'{task_name}' を開始しました。")
        except ScheduleTaskError as e:
            logger.error(f"'{task_name}' の開始に失敗しました。 {e}")
        except Exception:
            logger.exception(f"'{task_name}' の開始中に不明なエラーが発生しました。")

    logger.info("全てのタスクの登録と開始を完了しました。Discordのイベントループを開始します。")
    # discord.pyのループ
    discord_event_loop.start()

@tasks.loop(seconds=60)
async def discord_event_loop():
    """
    Discord.pyのスケジューラ
    """
    logger.debug("heartbeat")

    # ===== time keep =====
    # TODO 削除検討
    # async_scheduleを完全にNTPによって動作させられれば不要になる
    # 現在のntpとlocalの時刻と差分を表示
    nt = ntp_retrieve.get_locale_time()
    lt = datetime.now(ntp_retrieve.time_zone)
    logger.debug(f"NTP: {nt} LOCAL: {lt}")
    t_diff = abs(nt - lt)
    if t_diff >= timedelta(minutes=1):
        logger.warning(f"警告: {ntp_retrieve.ntp_host}とローカル時刻の差が1分以上あります！差分: {t_diff}")

    # ===== schedule =====
    # TODO 直近スケジュールの表示
    # tasks_objectを基にして行われる事になると思われる

    # ===== add execution =====

# ===== event handler =====
# 利用しそうなものを記述だけしておく
@client.event
async def on_message(message):
    """
    Message が更新イベントを受け取ったとき
    """

@client.event
async def on_resumed():
    """
    セッションを再開したとき
    """
    pass

@client.event
async def on_disconnect():
    """
    Discordから切断したときと、Discordへの接続の試行が失敗したとき
    """
    pass

if __name__ == "__main__":

    try:
        logger.info("vw-botを開始します。")
        client.run(DISCORD_TOKEN)

    except KeyboardInterrupt:
        logger.info("終了シグナルを受け取りました。vw-botの終了処理を開始します。")
        try:
            client.close()
            logger.info("正常終了")
            sys.exit(0)
        except:
            logger.error("closeを試みましたがエラーが発生しました。clientが正しく閉じられていない可能性があります。")
            logger.error("異常終了")
            sys.exit(1)
    except discord.errors.LoginFailure:
        logger.critical("ログインに失敗しました。`DISCORD_TOKEN`の値を確認してください。")
        logger.info("vw-botを終了します。")
        sys.exit(1)
    except Exception:
        logging.exception("不明なエラーが発生しました。")
        logger.info("vw-botを終了します。")
        sys.exit(1)

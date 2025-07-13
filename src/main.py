# -*- coding: utf-8 -*-
"""
プログラムの起動及び初期化とDiscordイベントによるコルーチンを規定
"""
from datetime import datetime, timedelta, time as dt_time
import logging
import os
import sys
import time

import discord
from discord.ext import tasks
from dotenv import load_dotenv
import schedule

from utils.actions import Bot
from utils.schedules import register_jobs
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
        if user_input == 'y':
            logger.info("vw-botの起動処理を続行します。")
            break
        elif user_input == 'n':
            logger.info("vw-botを終了します。")
            sys.exit(0)
        else:
            logger.info("無効な入力です。「y」または「n」を入力してください。")

# ===== environment =====
# .envの記述を環境変数へ登録
load_dotenv()
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
logger.info("discord.pyのclientを初期化しています。")
count = 0
while client.is_ready():
    count += 1
    time.sleep(3)
    if count > 10:
        logger.critical("長時間接続が確立出来ませんでした。")
        logger.critical("異常終了")
        sys.exit(1)
logger.info("discord.pyのclient接続が完了しました。")


@client.event
async def on_ready():
    """
    botがDiscordにログインしたとき
    """

    # botの動作を規定したクライアントを初期化
    bot = Bot(client, GUILD_ID, VC_CHANNEL_ID)

    # スケジュールを登録
    register_jobs(bot, JOIN_TIME, START_TIME, END_TIME)

    # discord.pyのループ
    discord_event_loop.start()

@tasks.loop(seconds=60)
async def discord_event_loop():
    """
    Discord.pyのスケジューラ
    """
    logger.debug("heartbeat")

    # ===== time keep =====
    # 現在のntpとlocalの時刻と差分を表示
    nt = ntp_retrieve.get_locale_time()
    lt = datetime.now(ntp_retrieve.time_zone)
    logger.debug(f"NTP: {nt} LOCAL: {lt}")
    t_diff = abs(nt - lt)
    if t_diff >= timedelta(minutes=1):
        logger.warning(f"警告: {ntp_retrieve.ntp_host}とローカル時刻の差が1分以上あります！差分: {t_diff}")

    # ===== schedule =====
    logger.debug("直近5件の登録スケジュール")
    all_jobs = schedule.get_jobs()
    all_jobs.sort(key=lambda x: x.next_run)
    last_five_jobs = all_jobs[-5:]
    for job in last_five_jobs:
        logger.debug(f"次の実行時間: {job.next_run} 実行間隔: {job.interval} 実行関数: {job.job_func.__name__}")
    # スケジューラ内容の実行 *ループ時間未満のタスクは実行出来ないので注意
    schedule.run_pending()

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
        logger.critical("ログインに失敗しました。`.env`の`DISCORD_TOKEN`の値を確認してください。")
        logger.info("vw-botを終了します。")
        sys.exit(1)
    except Exception:
        logging.exception("不明なエラーが発生しました。")
        logger.info("vw-botを終了します。")
        sys.exit(1)

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
import schedule

from utils.actions import Bot
from utils.schedules import register_jobs
from utils.ntp_client import NTPRetrieve
from utils.jobs import JST

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
# load_dotenv()
env_file = os.getenv("ENV_FILE", ".env.dev")
print(f"loading env from: {env_file}")
load_dotenv(dotenv_path=env_file)
if "prod" in env_file:
    ENV = "prod"
else:
    ENV = "dev"

logger.debug(f"環境変数ファイル:{env_file} 環境:{ENV}")

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
    logger.debug("直近5件の実行スケジュール")
    all_jobs = schedule.get_jobs()
    # 表示する実行jobを格納
    next_run_jobs = []

    for job in all_jobs:
        # vc_join_or_leaveは登録を無視する
        if job.job_func.__name__ == 'vc_join_or_leave':
            continue

        # 時刻指定されたjobで次回実行が予定されている場合はdailyであると仮定(良い実装ではない)
        if job.at_time and job.next_run:
            # 念のため日本時刻に変更
            next_run = JST.localize(job.next_run)
            # 実行の曜日を取得
            weekday = next_run.weekday()

            adjust_run = next_run
            # 土曜と日曜であれば無理矢理月曜日まで日付を足して調整(良い実装ではない)
            if weekday == 5:
                adjust_run += timedelta(days=2)
            elif weekday == 6:
                adjust_run += timedelta(days=1)

            next_run_jobs.append((adjust_run, job.job_func.__name__))

    # 実行時刻でソート
    next_run_jobs.sort(key=lambda x: x[0])

    # 直近5件を表示
    for next_run_time, job_name in next_run_jobs[:5]:
        logger.debug(f"次の実行時間: {next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')} 実行関数: {job_name}")

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

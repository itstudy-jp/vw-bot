import asyncio
import schedule
import time
import logging
from bot_tasks import (
    login_bot,
    logout_bot,
    notify_attendance,
    notify_start,
    notify_lunch,
    notify_leaving,
    notify_stop
)

# ===== ロギング設定 =====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("notification.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ===== スケジュール登録 =====
def schedule_jobs():
    logger.info("スケジュールを登録します。")

    # 9:00 出勤通知
    schedule.every().day.at("09:00").do(lambda: asyncio.create_task(notify_attendance()))

    # 毎時00分通知（10:00〜17:00）※12:00を除く
    for hour in range(10, 18):
        if hour != 12:
            schedule.every().day.at(f"{hour:02d}:00").do(lambda h=hour: asyncio.create_task(notify_start(hour=h)))

    # 毎時50分通知（9:50〜16:50）※11, 12, 17は除外
    for hour in range(9, 18):
        if hour not in [11, 12, 17]:
            schedule.every().day.at(f"{hour:02d}:50").do(lambda h=hour: asyncio.create_task(notify_stop(hour=h)))

    # 12:00 昼休憩通知
    schedule.every().day.at("12:00").do(lambda: asyncio.create_task(notify_lunch()))

    # 18:00 終了通知
    schedule.every().day.at("18:00").do(lambda: asyncio.create_task(notify_leaving()))

    logger.info("スケジュール登録が完了しました。")


# ===== 非同期でスケジュール監視 =====
async def scheduler_loop():
    logger.info("スケジューラーを開始します。")
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


# ===== メイン処理 =====
async def main():
    logger.info("Botの起動を開始します。")
    await login_bot()
    schedule_jobs()
    await scheduler_loop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("シャットダウン要求を受け取りました。Botをログアウトします。")
        asyncio.run(logout_bot())
        logger.info("Botを正常に停止しました。")

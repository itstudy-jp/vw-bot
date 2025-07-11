# -*- coding: utf-8 -*-
"""
bot動作時刻を規定
"""
from datetime import time as dt_time
import logging

import schedule
from pytz import timezone

from .jobs import vc_join_or_leave, notify_clock_in, notify_work_start, notify_break_start, notify_five_minutes_left, notify_hourly_task, notify_clock_out

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def register_jobs(bot, join_time, start_time, end_time):
    """
    スケジュールの登録
    """

    logger.info("スケジュール登録を開始します。")

    # vcへの参加または離脱
    schedule.every(1).minutes.do(vc_join_or_leave, bot=bot, j_time=join_time, e_time=end_time)

    # 始業通知
    schedule.every().day.at(str(start_time), timezone("Asia/Tokyo")).do(notify_clock_in, bot=bot)

    # 毎時00分作業開始通知
    for hour in range(start_time.hour+1, end_time.hour):

        # 12時は作業が行われない
        if hour != 12:

            register_hour = dt_time(hour)

            # 休憩なしでの作業
            if hour in [11, end_time.hour-1]:
                schedule.every().day.at(str(register_hour), timezone("Asia/Tokyo")).do(notify_hourly_task, bot=bot)

            else:
                schedule.every().day.at(str(register_hour), timezone("Asia/Tokyo")).do(notify_work_start, bot=bot, t=register_hour)

    # 毎時50分,5分前通知
    for hour in range(start_time.hour, end_time.hour-1):

        if hour not in [11, 12]:

            # 50分通知
            register_hour = dt_time(hour, 50)
            schedule.every().day.at(str(register_hour), timezone("Asia/Tokyo")).do(notify_break_start, bot=bot, t=register_hour)

            # 5分前通知
            register_5_minutes_earlier = dt_time(hour, 45)
            schedule.every().day.at(str(register_5_minutes_earlier), timezone("Asia/Tokyo")).do(notify_five_minutes_left, bot=bot)

        # 12時の5分前通知
        elif hour == 11:
            register_hour = dt_time(hour, 55)
            schedule.every().day.at(str(register_hour), timezone("Asia/Tokyo")).do(notify_five_minutes_left, bot=bot)

        # 昼休憩通知
        elif hour == 12:
            register_hour = dt_time(hour)
            schedule.every().day.at(str(register_hour), timezone("Asia/Tokyo")).do(notify_break_start, bot=bot, t=register_hour)

    # 終業5分前通知
    else:
        register_hour = dt_time(end_time.hour-1, 55)
        schedule.every().day.at(str(register_hour), timezone("Asia/Tokyo")).do(notify_five_minutes_left, bot=bot)

    # 終業通知
    schedule.every().day.at(str(end_time), timezone("Asia/Tokyo")).do(notify_clock_out, bot=bot)

    logger.info("スケジュール登録を完了しました。")

    logger.info("登録スケジュール一覧")
    all_jobs = schedule.get_jobs()
    all_jobs.sort(key=lambda x: x.next_run)
    for job in all_jobs:
        logger.info(f"次の実行時間: {job.next_run} 実行間隔: {job.interval} 実行関数: {job.job_func.__name__}")

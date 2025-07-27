# -*- coding: utf-8 -*-
"""
bot動作時刻を規定
"""
from datetime import datetime, time as dt_time
from functools import partial
import logging

from .async_scheduler import ScheduleTask
from .jobs import (
    vc_join_or_leave,
    notify_clock_in,
    notify_work_start,
    notify_break_start,
    notify_five_minutes_left,
    notify_hourly_task,
    notify_clock_out,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def register_jobs(bot, join_time, start_time, end_time):
    """
    スケジュールの登録
    """

    logger.info("スケジュール登録を開始します。")

    jobs = {}

    # vcへの参加または離脱
    jobs["vc_join_or_leave"] = ScheduleTask(
        partial(vc_join_or_leave, bot=bot, j_time=join_time, e_time=end_time),
        at_second=0,
    )

    # 始業通知
    jobs["notify_clock_in"] = ScheduleTask(
        partial(notify_clock_in, bot=bot),
        at_hour=int(start_time.hour),
        at_minute=int(start_time.minute),
        at_second=int(start_time.second),
    )

    # 毎時00分作業開始通知
    for hour in range(start_time.hour + 1, end_time.hour):

        # 12時は作業が行われない
        if hour != 12:

            register_hour = dt_time(hour)

            # 休憩なしでの作業
            if hour in [11, end_time.hour - 1]:
                jobs[f"notify_hourly_task-{hour}"] = ScheduleTask(
                    partial(notify_hourly_task, bot=bot),
                    at_hour=int(register_hour.hour),
                    at_minute=int(register_hour.minute),
                    at_second=int(register_hour.second),
                )

            else:
                jobs[f"notify_work_start-{hour}"] = ScheduleTask(
                    partial(notify_work_start, bot=bot, t=register_hour),
                    at_hour=int(register_hour.hour),
                    at_minute=int(register_hour.minute),
                    at_second=int(register_hour.second),
                )

    # 毎時50分,5分前通知
    for hour in range(start_time.hour, end_time.hour - 1):

        if hour not in [11, 12]:

            # 50分通知
            register_hour = dt_time(hour, 50)
            jobs[f"notify_break_start-{hour}"] = ScheduleTask(
                partial(notify_break_start, bot=bot, t=register_hour),
                at_hour=int(register_hour.hour),
                at_minute=int(register_hour.minute),
                at_second=int(register_hour.second),
            )

            # 5分前通知
            register_5_minutes_earlier = dt_time(hour, 45)
            jobs[f"notify_five_minutes_left-{hour}"] = ScheduleTask(
                partial(notify_five_minutes_left, bot=bot),
                at_hour=int(register_5_minutes_earlier.hour),
                at_minute=int(register_5_minutes_earlier.minute),
                at_second=int(register_5_minutes_earlier.second),
            )

        # 12時の5分前通知
        elif hour == 11:
            register_hour = dt_time(hour, 55)
            jobs[f"notify_five_minutes_left-{hour}"] = ScheduleTask(
                partial(notify_five_minutes_left, bot=bot),
                at_hour=int(register_hour.hour),
                at_minute=int(register_hour.minute),
                at_second=int(register_hour.second),
            )

        # 昼休憩通知
        elif hour == 12:
            register_hour = dt_time(hour)
            jobs[f"notify_break_start-{hour}"] = ScheduleTask(
                partial(notify_break_start, bot=bot, t=register_hour),
                at_hour=int(register_hour.hour),
                at_minute=int(register_hour.minute),
                at_second=int(register_hour.second),
            )

    # 終業5分前通知
    else:
        register_hour = dt_time(end_time.hour - 1, 55)
        jobs[f"notify_five_minutes_left-last"] = ScheduleTask(
            partial(notify_five_minutes_left, bot=bot),
            at_hour=int(register_hour.hour),
            at_minute=int(register_hour.minute),
            at_second=int(register_hour.second),
        )

    # 終業通知
    jobs[f"notify_clock_out"] = ScheduleTask(
        partial(notify_clock_out, bot=bot),
        at_hour=int(end_time.hour),
        at_minute=int(end_time.minute),
        at_second=int(end_time.second),
    )

    logger.info("スケジュール登録を完了しました。")

    logger.info("登録スケジュール一覧")

    display_jobs = []

    for job_name, task_instance in jobs.items():

        if job_name == "vc_join_or_leave":
            # vc_join_or_leave は at_second=0 で毎分実行されるので定数とする
            display_jobs.append((datetime.min.time(), job_name, "毎分0秒"))

        elif task_instance.at_time:
            display_jobs.append(
                (
                    task_instance.at_time,
                    job_name,
                    task_instance.at_time.strftime("%H:%M:%S"),
                )
            )

        else:
            display_jobs.append((datetime.min.time(), job_name, "時刻不明"))

    # 時刻でソート
    display_jobs.sort(key=lambda x: x[0])

    for _, job_name, time_str in display_jobs:
        logger.info(f"設定時刻: {time_str} 実行関数: {job_name}")

    return jobs

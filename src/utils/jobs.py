# -*- coding: utf-8 -*-
"""
スケジュールによるbot動作を規定
"""
import asyncio
from datetime import datetime, timedelta, timezone
import logging

from .messages import MESSAGES

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ===== locale =====
# TODO 要検証
# 異なるタイムゾーンで動作しているOSでも日本時間で動作
JST = timezone(timedelta(hours=+9), 'JST')
logger.info("TimeZoneをJSTに設定しました。")

# 日本時間での日付及び時刻オブジェクト
DT = datetime.now(JST)

# TODO jobのExceptionをキャッチ
# https://schedule.readthedocs.io/en/stable/exception-handling.html

def get_weekdays():
    """
   月曜日から金曜日であればflagをTrueで返す
    """
    flag = False
    # 月-金は0-5
    if DT.weekday() < 5:
        flag = True
    return flag

def vc_join_or_leave(bot, j_time, e_time):
    if get_weekdays():

        # 日本時間での現在時刻
        now_time = DT.time()
        # 規定時刻内であればVCに参加する
        if j_time <= now_time < e_time:
            asyncio.run_coroutine_threadsafe(bot.join_vc(), bot.client.loop)
        else:
            # 規定時刻外であれば切断する
            asyncio.run_coroutine_threadsafe(bot.leave_vc(), bot.client.loop)
    else:
        # 平日でなければ念のため切断をループさせておく
        asyncio.run_coroutine_threadsafe(bot.leave_vc(), bot.client.loop)


def notify_clock_in(bot):
    """
    始業
    """
    if get_weekdays():
        param = MESSAGES["clock_in"]
        msg = param["msg"]
        file_name = param["file_name"]
        asyncio.run_coroutine_threadsafe(bot.play_audio(file_name), bot.client.loop)
        asyncio.run_coroutine_threadsafe(bot.send_message(msg), bot.client.loop)

def notify_work_start(bot, t):
    """
    作業開始
    """
    if get_weekdays():
        param = MESSAGES["work_start"]
        msg = str(t.hour) + param["msg"]
        file_name = param["file_name"]
        asyncio.run_coroutine_threadsafe(bot.play_audio(file_name), bot.client.loop)
        asyncio.run_coroutine_threadsafe(bot.send_message(msg), bot.client.loop)

def notify_break_start(bot, t):
    """
    休憩開始
    """
    if get_weekdays():
        if t.hour == 12:
            param = MESSAGES["break_start"]["lunch"]
            msg = param["msg"]
            file_name = param["file_name"]
        else:
            param = MESSAGES["break_start"]["other"]
            msg = f"{t.hour}時{t.minute}分{param["msg"]}"
            file_name = param["file_name"]
        asyncio.run_coroutine_threadsafe(bot.play_audio(file_name), bot.client.loop)
        asyncio.run_coroutine_threadsafe(bot.send_message(msg), bot.client.loop)

def notify_five_minutes_left(bot):
    """
    作業時間終了まで残り5分
    """
    if get_weekdays():
        param = MESSAGES["five_minutes_left"]
        msg = param["msg"]
        file_name = param["file_name"]
        asyncio.run_coroutine_threadsafe(bot.play_audio(file_name), bot.client.loop)
        asyncio.run_coroutine_threadsafe(bot.send_message(msg), bot.client.loop)

def notify_hourly_task(bot):
    """
    1時間作業
    """
    if get_weekdays():
        param = MESSAGES["hourly_task"]
        msg = param["msg"]
        file_name = param["file_name"]
        asyncio.run_coroutine_threadsafe(bot.play_audio(file_name), bot.client.loop)
        asyncio.run_coroutine_threadsafe(bot.send_message(msg), bot.client.loop)

def notify_clock_out(bot):
    """
    終業
    """
    if get_weekdays():
        param = MESSAGES["clock_out"]
        msg = param["msg"]
        file_name = param["file_name"]
        asyncio.run_coroutine_threadsafe(bot.play_audio(file_name), bot.client.loop)
        asyncio.run_coroutine_threadsafe(bot.send_message(msg), bot.client.loop)
        asyncio.run_coroutine_threadsafe(bot.leave_vc(), bot.client.loop)

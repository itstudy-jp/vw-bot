# -*- coding: utf-8 -*-
"""
スケジュールによるbot動作を規定
"""
from datetime import datetime
import logging

from pytz import timezone

from .messages import MESSAGES

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# ===== locale =====
# TODO 要検証
# 異なるタイムゾーンで動作しているOSでも日本時間で動作
JST = timezone("Asia/Tokyo")
logger.info("TimeZoneをJSTに設定しました。")


# TODO jobのExceptionをキャッチ
# https://schedule.readthedocs.io/en/stable/exception-handling.html
def get_now_time():
    """
    # 日本時間での日付及び時刻オブジェクト
    """
    return datetime.now(JST)


def get_weekdays():
    """
    月曜日から金曜日であればTrueを返す
    """
    dt = get_now_time()
    # 月-金は0-4
    if dt.weekday() < 5:
        return True
    else:
        return False


async def simple_operation(bot):
    """
    簡易テスト用
    vcへ接続してメッセージの投稿と音声ファイルの再生を行う
    音声ファイルが最後まで再生されたらvcから切断する
    """

    await bot.join_vc()
    param = MESSAGES["clock_in"]
    msg = param["msg"]
    file_name = param["file_name"]
    await bot.send_message(msg)
    await bot.play_audio(file_name)
    await bot.leave_vc()


async def vc_join_or_leave(bot, j_time, e_time):
    """
    規定時刻内であればVCに参加し、規定時刻外であればVCから切断をループ
    """
    if get_weekdays():

        # example: 2025-07-13 19:25:12.880298+09:00
        dt = get_now_time()
        # 日本時間での現在時刻 example: 19:25:12.880298
        now_time = dt.time()
        # 規定時刻内であればVCに参加する
        if j_time <= now_time < e_time:
            await bot.join_vc()
        else:
            # 規定時刻外であれば切断する
            await bot.leave_vc()
    else:
        # 平日でなければ念のため切断をループさせておく
        await bot.leave_vc()


async def notify_clock_in(bot):
    """
    始業
    """
    if get_weekdays():
        param = MESSAGES["clock_in"]
        msg = param["msg"]
        file_name = param["file_name"]
        await bot.send_message(msg)
        await bot.play_audio(file_name)


async def notify_work_start(bot, t):
    """
    作業開始
    """
    if get_weekdays():
        param = MESSAGES["work_start"]
        msg = str(t.hour) + param["msg"]
        file_name = param["file_name"]
        await bot.send_message(msg)
        await bot.play_audio(file_name)


async def notify_break_start(bot, t):
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
            msg = f'{t.hour}時{t.minute}分{param["msg"]}'
            file_name = param["file_name"]
        await bot.send_message(msg)
        await bot.play_audio(file_name)


async def notify_five_minutes_left(bot):
    """
    作業時間終了まで残り5分
    """
    if get_weekdays():
        param = MESSAGES["five_minutes_left"]
        msg = param["msg"]
        file_name = param["file_name"]
        await bot.send_message(msg)
        await bot.play_audio(file_name)


async def notify_hourly_task(bot):
    """
    1時間作業
    """
    if get_weekdays():
        param = MESSAGES["hourly_task"]
        msg = param["msg"]
        file_name = param["file_name"]
        await bot.send_message(msg)
        await bot.play_audio(file_name)


async def notify_clock_out(bot):
    """
    終業
    """
    if get_weekdays():
        param = MESSAGES["clock_out"]
        msg = param["msg"]
        file_name = param["file_name"]
        await bot.send_message(msg)
        await bot.play_audio(file_name)
        await bot.leave_vc()

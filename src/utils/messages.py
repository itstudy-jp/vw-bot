# -*- coding: utf-8 -*-
"""
botの発話に必要な定数を規定
"""
MESSAGES = {
    "clock_in": {
        "msg": "おはようございます。本日も頑張りましょう。",
        "file_name": "attendance.wav"
    },
    "work_start": {
        "msg": "時になりました。開始してください。",
        "file_name": "start.wav"
    },
    "break_start": {
        "lunch": {
            "msg": "お疲れ様です。お昼になりました。",
            "file_name": "lunch.wav"
        },
        "other": {
            "msg": "になりました。休憩です。",
            "file_name": "stop.wav"},
        },
    "five_minutes_left": {
        "msg": "作業終了まで残り5分です。",
        "file_name": "5_minutes_left.wav"
    },
    "hourly_task": {
        "msg": "ここからの作業時間は1時間です。開始してください。",
        "file_name": "1_hour_start.wav"
    },
    "clock_out": {
        "msg": "本日もお疲れ様でした。",
        "file_name": "leaving.wav"
    },
}

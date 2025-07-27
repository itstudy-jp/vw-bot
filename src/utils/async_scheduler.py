import asyncio
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta, timezone, time as dt_time
import logging
from typing import Final

import discord
import ntplib

logger: Final = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class AioNTP:
    """非同期に対応したNTPクライアント"""

    NTP_HOST: Final = "pool.ntp.org"
    TIME_ZONE: Final = timezone(timedelta(hours=+9))

    def __init__(self):
        self.ntp_client = ntplib.NTPClient()
        self.ntp_host = self.NTP_HOST
        self.time_zone = self.TIME_ZONE

    async def ntp_request(self) -> ntplib.NTPStats:
        """非同期にNTPのリクエストを送る。"""

        def fn() -> ntplib.NTPStats:
            return self.ntp_client.request(self.ntp_host, version=4)

        # run_in_executorはfnに対して*argsの引数を求めているが、渡すものがないので型チェックを無視する
        return await asyncio.get_running_loop().run_in_executor(None, fn)  # type: ignore[call-arg]

    async def get_locale_time(self) -> datetime:
        """NTPを用いて、現在時刻を取得する。"""
        # version type rfc2030 and rfc4330
        response = await self.ntp_request()
        unix_time = response.tx_time
        dt_object = datetime.fromtimestamp(unix_time, timezone.utc)

        # 指定されたtimezoneの時刻オブジェクトに変更
        selected_time_zone = dt_object.astimezone(self.time_zone)

        return selected_time_zone


def get_next_datetime(
    hour: int | None = None,
    minute: int | None = None,
    second: int | None = None,
    *,
    now: datetime | None = None,
) -> datetime:
    """指定された時・分・秒になる、次の時刻を算出する。"""
    now = now or datetime.now()

    # 引数で指定された条件を辞書にまとめる
    replace_args = {}
    if hour is not None:
        replace_args["hour"] = hour
    if minute is not None:
        replace_args["minute"] = minute
    if second is not None:
        replace_args["second"] = second

    if not replace_args:
        raise ValueError("少なくとも、どれか一つの引数は指定してください。")

    # まず、今日の時刻で候補を計算（指定のない部分は現在の時刻を利用）
    candidate_time = now.replace(**replace_args, microsecond=0)

    # 候補時刻が現在時刻より前か同じ場合は、未来の時刻になるまで時間を進める。（繰り上がり）
    if candidate_time <= now:
        if hour is not None:
            candidate_time += timedelta(days=1)
        elif minute is not None:
            candidate_time += timedelta(hours=1)
        else:
            candidate_time += timedelta(minutes=1)

    return candidate_time


class ScheduleTaskError(Exception):
    """``ScheduleTask``のタスクの``start``または``stop`で使うエラー"""


class ScheduleTask:
    """特定の時間にジョブを実行するスケジュールタスク"""

    def __init__(
        self,
        job: Callable[[], Awaitable],
        *,
        at_hour: int | None = None,
        at_minute: int | None = None,
        at_second: int | None = None,
        on_error: Callable[[Exception], Awaitable] | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
        now: Callable[[], Awaitable[datetime]] | None = None,
    ) -> None:
        self._job = job
        self._task = None

        self.at_second = at_second
        self.at_minute = at_minute
        self.at_hour = at_hour

        async def _default_on_error(_) -> None:
            logger.exception("ループ実行中にエラーが発生。")

        self.on_error = on_error or _default_on_error
        self._now = now or AioNTP().get_locale_time
        self.loop = loop or asyncio.get_running_loop()

    @property
    def at_time(self) -> dt_time | None:
        """ジョブが設定されている時間を datetime.time オブジェクトとして返す"""
        # TODO 不足している処理の実装
        # 一時的に時分秒が全て登録されているものだけ返す
        # 0はFalseになるのでallは使えない事に留意
        if (
            self.at_hour is not None
            and self.at_minute is not None
            and self.at_second is not None
        ):
            return dt_time(self.at_hour, self.at_minute, self.at_second)
        # elif self.at_minute is not None and self.at_second is not None:
        #     return dt_time(0, self.at_minute, self.at_second)
        # elif self.at_second is not None:
        #     return dt_time(0, 0, self.at_second)
        return None

    def start(self) -> None:
        """ジョブを実行するループを開始する。"""
        if self._task is not None:
            raise ScheduleTaskError("既に開始しています。")

        self._task = self.loop.create_task(self._loop())

    def stop(self) -> asyncio.Task[None]:
        """ジョブを実行するループを停止する。"""
        if self._task is None:
            raise ScheduleTaskError("既に停止しています。")

        self._task.cancel()
        task = self._task
        self._task = None

        return task

    async def get_next_job_datetime(self) -> datetime:
        """次にジョブを実行すべき時刻を取得する。"""
        now = await self._now()
        next_run_time = get_next_datetime(
            self.at_hour, self.at_minute, self.at_second, now=now
        )

        return next_run_time

    async def _loop(self) -> None:
        while True:
            # 次のジョブ実行時刻まで待機する。
            next_job_datetime = await self.get_next_job_datetime()
            # TODO 時刻のNTP基準化
            # ホストOS時刻での実行ではなくNTP基準にするためNTPとホストOSの差分を取る
            # next_job_datetimeをそのまま引き渡すのではなく、差分を増減した時刻を渡す事でNTP時刻に合致させる
            # 実行はホストOSの時刻に依存する
            await discord.utils.sleep_until(next_job_datetime)

            # ジョブを実行する。
            try:
                await self._job()
            except Exception as e:
                # TODO タスクの再登録処理
                # エラーでタスクが停止した場合にそのタスクは失われてしまう
                # ScheduleTaskErrorを受けて再度タスクを登録する処理が必要
                await self.on_error(e)
                break


async def main() -> None:
    """動作確認用の関数"""

    async def loop_00s_task() -> None:
        print("00秒ちょうど")

    # "00秒ちょうど" を毎分0秒時に実行する
    task = ScheduleTask(loop_00s_task, at_second=0)
    task.start()

    # 180sで停止
    await asyncio.sleep(60 * 3)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

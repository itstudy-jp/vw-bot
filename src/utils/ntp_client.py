# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timezone, timedelta
import sys

import ntplib

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

NTP_HOST = 'pool.ntp.org'
TIME_ZONE = timezone(timedelta(hours=+9))

class NTPRetrieve:
    def __init__(self):
        self.ntp_client = ntplib.NTPClient()
        self.ntp_host = NTP_HOST
        self.time_zone = TIME_ZONE

    def get_locale_time(self):
        try:
            # version type rfc2030 and rfc4330
            response = self.ntp_client.request(self.ntp_host, version=4)
            unix_time = response.tx_time
            dt_object = datetime.fromtimestamp(unix_time, timezone.utc)
            # 指定されたtimezoneの時刻オブジェクトに変更
            selected_time_zone = dt_object.astimezone(self.time_zone)
            return selected_time_zone
        except Exception:
            logger.exception("NTPサーバーからの時刻取得に失敗しました。")
            sys.exit(1)

def main():
    client = NTPRetrieve()
    print(client.get_locale_time())

if __name__ == "__main__":
    main()

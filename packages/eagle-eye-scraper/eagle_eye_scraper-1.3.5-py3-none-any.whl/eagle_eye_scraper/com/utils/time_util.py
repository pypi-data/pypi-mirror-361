from datetime import datetime

from pytz import timezone


class TimeUtils:
    # 创建上海时区（东八区）
    shanghai_tz = timezone('Asia/Shanghai')

    @staticmethod
    def get_now_time():
        """
        获取上海时区（东八区）的当前时间。
        Returns:
            datetime: 上海时区的当前时间。
        """
        return datetime.now(TimeUtils.shanghai_tz)

    @staticmethod
    def get_now_ts():
        """
        获取上海时区（东八区）的当前时间戳（毫秒级）。
        Returns:
            int: 当前时间的时间戳（自1970年1月1日以来的毫秒数）。
        """
        now_time = datetime.now(TimeUtils.shanghai_tz)
        return int(now_time.timestamp() * 1000)

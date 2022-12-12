from datetime import datetime as datetime
from typing import Tuple

__all__ = ["today", "calc_time"]


def today() -> datetime:

    return datetime.now()


def calc_time(time0: datetime, time1: datetime) -> Tuple[int, int, int, int, int]:
    _second: int = (time1 - time0).seconds
    _minute: float = _second / 60
    _hour: float = _minute / 60
    _day: float = _hour / 24
    _month: float = _day / 30
    second: int = int(_second % 60)
    minute: int = int(_minute % 60)
    hour: int = int(_hour % 24)
    day: int = int(_day % 30)
    month: int = int(_month)

    return month, day, hour, minute, second

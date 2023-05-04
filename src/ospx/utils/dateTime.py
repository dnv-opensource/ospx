from datetime import datetime as datetime
from typing import Tuple

__all__ = ["calc_time"]


def calc_time(time0: datetime, time1: datetime) -> Tuple[int, int, int, int, int]:
    """Calculate the time delta between time0 and time1.

    Calculates the time delta between time0 and time1 and
    returns the result as a tuple of integers representing the number of
    months, days, hours, minutes and seconds
    the time delta constitutes.

    Parameters
    ----------
    time0 : datetime
        start time
    time1 : datetime
        end time

    Returns
    -------
    Tuple[int, int, int, int, int]
        tuple of integers representing the number of
        months, days, hours, minutes and seconds
        the time delta constitutes.
    """
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

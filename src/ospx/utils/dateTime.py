from datetime import datetime

__all__ = ['today', 'calc_time']


def today():

    return datetime.now()


def calc_time(time0, time1):
    second = time1 - time0
    minute = second / 60
    hour = minute / 60
    day = hour / 24
    month = day / 30
    second = int(second % 60)
    minute = int(minute % 60)
    hour = int(hour % 24)
    day = int(day % 30)
    month = int(month)

    return month, day, hour, minute, second

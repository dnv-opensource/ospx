from datetime import datetime

__all__ = ['today', 'calcTime']


def today():

    return datetime.now()


def calcTime(time0, time1):
    deltaT = time1 - time0
    sec = deltaT
    minu = sec / 60
    h = minu / 60
    d = h / 24
    M = d / 30
    sec = int(sec % 60)
    minu = int(minu % 60)
    h = int(h % 24)
    d = int(d % 30)
    M = int(M)

    return M, d, h, minu, sec

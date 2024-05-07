import datetime


def ts_to_dt(tt):
    dt = datetime.datetime.fromtimestamp(tt)
    return dt


def dt_to_ts(dt):
    tt = dt.timestamp()
    return tt

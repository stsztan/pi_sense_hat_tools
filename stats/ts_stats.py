import numpy as np


def ts_stats(ts):
    '''
    ts_stats describes equitemporal time series with the following parameters:
        open, close, low, high, mean, stdev, median

    Parameters
    ----------
    ts : array-like object
        ts is time series data supposedly equidistant sampling in time

    Returns
    -------
    c_stats : dict (json compatible dictionary)
        JSON compliant dictionary is returned:
            open: first element
            close: last element
            low: minimum value
            high: maximum value
            mean: arithmetical mean
            stdev: standard deviation
            median: median of values

    '''
    o = ts[0]
    c = ts[-1]
    s = np.array(ts)
    l = s.min()
    h = s.max()
    m = s.mean()
    d = s.std()
    n = np.median(ts)
    c_stats = {
        'open': o,
        'close': c,
        'low': l,
        'high': h,
        'mean': m,
        'stdev': d,
        'median': n,
    }
    return c_stats

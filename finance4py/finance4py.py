# -*- coding: utf-8 -*-

import numpy as np
from pandas import DataFrame
import pandas as pd

def bbands(close, window=30, num_std=2):
    """

    :param close:
    :param window:
    :param num_std:
    :return:
    """
    average = close.rolling(window=window, center=False).mean()
    std = close.rolling(window=window, center=False).std()
    upband = average + (std*num_std)
    dnband = average - (std*num_std)
    boll_bands = DataFrame.from_dict({
        'close_average': np.round(average, 3),
        'bb_upper': np.round(upband, 3),
        'bb_lower': np.round(dnband, 3)
    })
    return boll_bands


def true_range(high, low, close):
    """
    True Range (TR), which is defined as the greatest of the following:

    - Current High less the current Low
    - Current High less the previous Close (absolute value)
    - Current Low less the previous Close (absolute value)

    :param high: Pandas Series
    :param low: Pandas Series
    :param close: Pandas Series
    :return: TR: Dataframe representing the true range calculated as above
    """
    tr = DataFrame()
    tr['TR1'] = abs(high - low)
    tr['TR2'] = abs(high - close.shift())
    tr['TR3'] = abs(low - close.shift())
    tr['TR'] = tr[['TR1', 'TR2', 'TR3']].max(axis=1)

    return tr


def average_true_range(high, low, close, window=14):
    """
    Average True range. It's an indicator that measure volatility.

    https://stockcharts.com/school/doku.php?id=chart_school:\
    technical_indicators:average_true_range_atr

    https://en.wikipedia.org/wiki/Average_true_range

    :param stock: pandas DataFrame
    :param window: int.
    :return:
    """
    tr = true_range(high, low, close,)
    atr = [np.nan] * tr.shape[0]
    atr[window] = tr['TR'].iloc[:window].mean()
    for i in range(window+1, len(atr)):
        atr[i] = (atr[i-1] * (window - 1) + tr['TR'].iloc[i]) / window
    tr['ATR'] = atr
    return tr


def rsi(close, window=14):
    """

    :param close:
    :param window:
    :return:
    """
    delta = close.diff()

    up, down = delta.copy(), delta.copy()

    # can't remember why did this
    up[up < 0] = 0
    down[down > 0] = 0

    # TODO: Is it correct to use exponential moving average?
    roll_up = up.ewm(ignore_na=False, min_periods=0, adjust=True, com=window)\
        .mean()
    roll_down = down.abs().ewm(ignore_na=False, min_periods=0, adjust=True,
                               com=window).mean()

    # This is deprecated in pandas 0.19.1
    # roll_up = pd.stats.moments.ewma(up, window)
    # roll_down = pd.stats.moments.ewma(down.abs(), window)

    rs = roll_up / roll_down
    rsi_series = 100.0 - (100.0 / (1.0 + rs))
    rsi_series.rename('RSI', inplace=True)
    return rsi_series


def macd(close, n_fast=12, n_slow=26):
    """

    :param close:
    :param n_fast:
    :param n_slow:
    :return:
    """
    # Vengono calcolate 2 medie (exponential moving average) con periodi di
    # 12 e 26 giorni
    # IL MACD e' la differenza di queste 2 medie. Mentre la curva che da il
    # segnale di acquisto e' la EMA del MACD a 9 giorni
    ema_fast = close.ewm(ignore_na=False, min_periods=n_slow-1, adjust=True,
                         com=n_fast).mean()
    ema_slow = close.ewm(ignore_na=False, min_periods=n_slow-1, adjust=True,
                         com=n_slow).mean()

    suffix = '{0}_{1}'.format(str(n_fast), str(n_slow))
    macd_df = pd.Series(ema_fast - ema_slow, name='MACD_{0}'.format(suffix))
    macd_sign = pd.Series(macd_df.ewm(ignore_na=False, com=9, adjust=True,
                                      min_periods=8).mean(),
                          name='MACDsign_{0}'.format(suffix))
    macd_diff = pd.Series(macd_df - macd_sign, name='MACDdiff_{0}'.format(suffix))
    df = macd_df.to_frame().join(macd_sign.to_frame()).join(macd_diff.to_frame())
    return df

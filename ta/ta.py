from typing import Callable, NamedTuple
import numpy as np


class CandleBodyTypeT(NamedTuple):
    Timestamp: int = 0
    Open: int = 1
    High: int = 2
    Low: int = 3
    Close: int = 4
    Volume: int = 5
    Nothing: int = 6

CandleBodyType = CandleBodyTypeT()

def sma_tv(
    source: np.array,
    length: int,
) -> np.array:
    """
    [Simple Moving average from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.sma)

    Parameters
    ----------
    source : np.array
        Values to process
    length : int
        Number of bars

    Returns
    -------
    np.array
        sma
    """
    sma = np.full_like(source, np.nan)
    len_minus_one = length - 1

    starting_index = source[np.isnan(source)].size + len_minus_one

    for i in range(starting_index, source.size):
        sma[i] = source[i - len_minus_one : i + 1].mean()

    return sma



def true_range_tv(
    candles: np.array,
) -> np.array:
    """
    [True Range from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.tr)

    Parameters
    ----------
    candles : np.array
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume]

    Returns
    -------
    np.array
        true_range
    """
    high = candles[:, CandleBodyType.High]
    low = candles[:, CandleBodyType.Low]
    prev_close = np.roll(candles[:, CandleBodyType.Close], 1)
    prev_close[0] = np.nan
    true_range = np.maximum(
        np.maximum(
            high - low,
            np.absolute(high - prev_close),
        ),
        np.absolute(low - prev_close),
    )
    return true_range


def rma_tv(
    source: np.array,
    length: int,
) -> np.array:
    """
    [Relative strength index Moving average from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.rma)

    Parameters
    ----------
    source : np.array
        Values to process
    length : int
        Number of bars

    Returns
    -------
    np.array
        rma
    """
    alpha = 1 / length

    starting_index = source[np.isnan(source)].size + length

    rma = np.full_like(source, np.nan)
    rma[starting_index - 1] = source[starting_index - length : starting_index].mean()

    for i in range(starting_index, source.size):
        rma[i] = alpha * source[i] + (1 - alpha) * rma[i - 1]

    return rma


def atr_tv(
    candles: np.array,
    length: int,
    smoothing_type: Callable = rma_tv,
) -> np.array:
    """
    [Average true range smoothing from tradingview](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.atr)

    Parameters
    ----------
    candles : np.array
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume]
    length : int
        Number of bars
    smoothing_type : Callable
        function to process the smoothing of the atr

    Returns
    -------
    np.array
        atr
    """
    true_range = true_range_tv(candles=candles)
    atr = smoothing_type(source=true_range, length=length)
    return atr



def supertrend_tv(
    candles: np.array,
    atr_length: int,
    factor: int,
) -> tuple[np.array, np.array]:
    """
    [Super Trend](https://www.tradingview.com/pine-script-reference/v5/#fun_ta.supertrend)

    Parameters
    ----------
    candles : np.array
        2-dim np.array with columns in the following order [timestamp, open, high, low, close, volume]
    atr_length : int
        Number of bars
    factor : int
        The multiplier by which the ATR will get multiplied

    Returns
    -------
    tuple[np.array, np.array]
        super_trend, direction
    """
    atr = atr_tv(candles=candles, length=atr_length)
    source = (candles[:, CandleBodyType.High] + candles[:, CandleBodyType.Low]) / 2
    close = candles[:, CandleBodyType.Close]
    super_trend = np.full_like(close, np.nan)
    direction = np.full_like(close, np.nan)

    upper_band = source[atr_length] + factor * atr[atr_length]
    lower_band = source[atr_length] - factor * atr[atr_length]
    super_trend[atr_length] = upper_band
    direction[atr_length] = 1

    for i in range(atr_length + 1, candles.shape[0]):
        current_source = source[i]
        current_atr = atr[i]
        current_close = close[i]

        prev_close = close[i - 1]

        # Lower band
        prev_lower_band = lower_band
        lower_band = current_source - factor * current_atr

        if lower_band <= prev_lower_band and prev_close >= prev_lower_band:
            lower_band = prev_lower_band

        # Upper Band
        prev_upper_band = upper_band
        upper_band = current_source + factor * current_atr

        if upper_band >= prev_upper_band and prev_close <= prev_upper_band:
            upper_band = prev_upper_band

        direction[i] = -1
        super_trend[i] = lower_band

        if super_trend[i - 1] == prev_upper_band:
            if current_close <= upper_band:
                direction[i] = 1
                super_trend[i] = upper_band
        else:
            if current_close < lower_band:
                direction[i] = 1
                super_trend[i] = upper_band
    return super_trend, direction


def index_tv(index=0):
    if index < 0:
        raise ValueError("Index must be greater than or equal to 0")
    actual_index = -1
    if index == 0:
        return actual_index
    for _ in range(index):
        actual_index -= 1
    return actual_index

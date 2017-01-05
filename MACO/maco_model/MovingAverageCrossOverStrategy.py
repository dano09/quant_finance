#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016
Design inspired by articles on Quantstart.com
"""
from Strategy import Strategy
import pandas as pd
import numpy as np


class MovingAverageCrossOverStrategy(Strategy):
    """
    MACO Paramters
    symbol: String - A stock symbol on which to form a strategy on.
    bars: Dataframe - OHLCAV data for symbol.
    short_lookback: Int - Shorter Moving Average look-back window.
    long_lookback: Int - Longer Moving Average look-back window."""

    def __init__(self, symbol, bars, short_lookback, long_lookback):
        self.symbol = symbol
        self.bars = bars
        self.short_lookback = short_lookback
        self.long_lookback = long_lookback

    def generate_signals(self):
        """
        Creates the signals used in the MACO strategy
        :return: Dataframe - time-series of signals for the strategy
        """

        # Signals are only accurate after the shorter moving average window has been reached
        start_signals = self.short_lookback

        # Index will be a time-series
        signals = pd.DataFrame(index=self.bars.index)

        # Need the moving averages before we can determine signals
        signals['signal'] = 0.0

        # Create and add shorter moving average to dataframe
        signals['short_mavg'] = pd.rolling_mean(self.bars['adj_close_price'],
                                                self.short_lookback, min_periods=1)
        # Create and add longer moving average to dataframe
        signals['long_mavg'] = pd.rolling_mean(self.bars['adj_close_price'],
                                               self.long_lookback, min_periods=1)

        # Every day following the start_signals date a signal will be assigned 1 if the shorter
        # moving average is higher than the longer moving average and 0 otherwise
        signals['signal'][start_signals:] = \
            np.where(signals['short_mavg'][start_signals:]
                     > signals['long_mavg'][start_signals:], 1.0, 0.0)

        '''
        The difference between the signals will be used to indicate a trade to execute.
        When the signal changes from 0.0 to 1.0, the position will be assigned a 1.0,
        and when its 1.0 to 0.0 the position will be assigned a -1.0. When there is no
        change in signal the position will be 0
        '''
        signals['positions'] = signals['signal'].diff()

        return signals




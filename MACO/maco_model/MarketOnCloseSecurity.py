#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""


class MarketOnCloseSecurity():
    """Encapsulates the notion of a portfolio of positions based
    on a set of signals as provided by a Strategy.

    Requires:
    symbol: string - A stock symbol which forms the basis of the portfolio
    bars: dataframe -  daily OHLCAV price data
    signals: dataframe -  Signals (1, 0, -1) indicating buy/sell transactions
   """

    def __init__(self, symbol, bars, signals):
        self.symbol = symbol
        self.bars = bars
        self.signals = signals

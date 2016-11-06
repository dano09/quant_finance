#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""


class MarketOnCloseSecurity():
    """Encapsulates the notion of a portfolio of positions based
    on a set of signals as provided by a Strategy.

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
   """

    def __init__(self, symbol, bars, signals):
        self.symbol = symbol
        self.bars = bars
        self.signals = signals

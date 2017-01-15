#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Justin Dano 10/23/2016
# Design inspired by articles on Quantstart.com

from abc import ABCMeta, abstractmethod


class Portfolio(object):
    """
    Abstract Base class for a portfolio. Currently it includes logic to generate positions
    based on the Strategy class, and to perform backtesting. Portfolios will contain a
    basket of stocks with their respected holdings, cash total and any returns.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_cash_change(self):
        """Derives the daily transaction of cash to assets and visa versa."""
        raise NotImplementedError("Must implement get_cash_change()!")

    @abstractmethod
    def get_holdings(self):
        """Derives the daily value of all assets in the portfolio."""
        raise NotImplementedError("Must implement get_holdings()!")

    @abstractmethod
    def backtest_portfolio(self):
        """Calculates cash and returns after each bar of data. Logic
        to execute pseudo-orders is included."""
        raise NotImplementedError("Must implement backtest_portfolio()!")

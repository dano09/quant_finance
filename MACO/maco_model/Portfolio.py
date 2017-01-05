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
    def backtest_portfolio(self):
        """Provides the necessary functionality to execute pseudo-orders,
        and dynamically update the portfolio after each bar of data.
        The portfolio should also be able to calculate returns and report
        total equity."""
        raise NotImplementedError("Must implement backtest_portfolio()!")
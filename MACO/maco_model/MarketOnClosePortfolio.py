#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
from Portfolio import Portfolio
import pandas as pd


class MarketOnClosePortfolio(Portfolio):
    """A portfolio with logic to perform backtesting.

    Requires:
    symbol - A stock symbol which forms the basis of the portfolio.
    bars - A DataFrame of bars for a symbol set.
    signals - A pandas DataFrame of signals (1, 0, -1) for each symbol.
    initial_capital - The amount in cash at the start of the portfolio."""

    def __init__(self, market_on_close_securities, initial_capital=100000.0):
        self.market_on_close_securities = market_on_close_securities
        self.initial_capital = float(initial_capital)

        #loop through each MOCS (market_on_close_security) to calculate positions
        #TODO: Create buy shares method (maybe use tuple class thing or try w/o)
        securities = {
            security.symbol: 100 * security.signals['signal'] # This strategy buys 100 shares
            for security in market_on_close_securities
        }
        self.positions = pd.DataFrame(securities)

    def calculate_cash(self, poss_diff):
        """Calculates the value of shares in USD

        :param poss_diff: Dataframe - The change is shares for a given day
        :return: Series - Cash value of all shares for every day
        """
        total_cash = 0
        for s in self.market_on_close_securities:
            total_cash += (poss_diff[s.symbol] * s.bars['close_price'].astype(float))

        print "done calculate cash"
        return self.initial_capital - total_cash.cumsum()

    def calculate_returns(self, portfolio, pos_diff):
        portfolio['holdings'] = portfolio.sum(axis=1)
        portfolio['cash'] = self.calculate_cash(pos_diff)
        portfolio['cash'][0] = self.initial_capital
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']
        portfolio['returns'] = portfolio['total'].pct_change()

    def generate_positions(self):
        # Initialize index for Portfolio Dataframe. Picking index 0 was arbitrary they all have same index length
        portfolio = pd.DataFrame(index=self.market_on_close_securities[0].bars.index)

        for security in self.market_on_close_securities:
            portfolio_series = self.positions[security.symbol] * security.bars['close_price'].astype(float)
            pos_diff = self.positions.diff()
            portfolio[security.symbol] = portfolio_series.values

        return portfolio, pos_diff

    def backtest_portfolio(self):
        """
        Creates portfolio and performs back testing
        :return: Dataframe - Portfolio of daily stock holdings and returns
        """
        # Sum holdings from each company
        portfolio, pos_diff = self.generate_positions()
        # Derive metrics for the portfolio
        self.calculate_returns(portfolio, pos_diff)

        return portfolio


#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
from Portfolio import Portfolio
import pandas as pd

from decimal import Decimal, InvalidOperation


class MarketOnClosePortfolio(Portfolio):
    """A portfolio with logic to perform backtesting.

    Requires:
    market_on_close_securities: list (MarketOnCloseSecurity) - Each MOCS contains ticker symbol, price data (dataframe),
     and signals (dataframe).
    trade_amount : int - Number of shares to be bought or sold.
    initial_capital: int - The amount in cash at the start of the portfolio.
    """
    def __init__(self, market_on_close_securities, trade_amount=100, initial_capital=100000.0):
        self.market_on_close_securities = market_on_close_securities
        self.trade_amount = trade_amount
        self.initial_capital = float(initial_capital)

        # Loop through each MOCS (market_on_close_security) to calculate positions
        securities = self.buy_shares()
        self.positions = pd.DataFrame(securities)

        # Derive daily cash transition
        self.cash_change = self.get_cash_change()

        # Calculate asset values
        self.holdings = self.get_holdings()

    def buy_shares(self):
        # Create a dictionary for each security in our portfolio. Each security will
        # map to a dataframe that holds the positions for buying and selling
        securities = {
            security.symbol: self.trade_amount * security.signals['positions']
            for security in self.market_on_close_securities
        }
        return securities

    def get_cash_change(self):
        """
        Calculate daily cash to be transacted every day. Cash change depends on
        the position (either buy or sell) multiplied by the adjusted closing price
        of the equity multiplied by the trade amount.
        :return: Dataframe
        """
        cash_change = pd.DataFrame(index=self.positions.index)
        try:

            for security in self.market_on_close_securities:
                # Perform calculation for cash change
                cash_change[security.symbol] = security.signals['positions'] * security.bars['adj_close_price'].astype(float) * self.trade_amount

        except InvalidOperation as e :
            print("Invalid input : " + str(e))

        # Sum each equities change in cash
        cash_change['cash_change'] = cash_change.sum(axis=1)

        return cash_change

    def get_holdings(self):
        """
        Calculates daily holdings for all assets in portfolio
        :return: Dataframe
        """
        holdings = pd.DataFrame(index=self.positions.index)
        try:
            for security in self.market_on_close_securities:
                # Perform holdings calculation for each asset
                holdings[security.symbol] = security.signals['signal'] * security.bars['adj_close_price'].astype(float) * self.trade_amount

        except InvalidOperation as e:
            print("Invalid input : " + str(e))

        # Calculates total holdings
        holdings['holdings'] = holdings.sum(axis=1)
        return holdings

    def backtest_portfolio(self):
        """
        Creates portfolio and performs and determines daily value of portfolio
        :return: Dataframe - Portfolio of daily stocks with holdings and cash
        """
        portfolio = self.holdings
        portfolio['cash'] = self.initial_capital - self.cash_change['cash_change'].cumsum()
        portfolio['cash'][0] = self.initial_capital
        portfolio['total'] = portfolio['cash'] + portfolio['holdings']

        return portfolio





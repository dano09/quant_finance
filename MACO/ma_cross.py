#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""

from MACO.Plotter import Plotter
from MarketOnClosePortfolio import MarketOnClosePortfolio
from MarketOnCloseSecurity import MarketOnCloseSecurity
from MovingAverageCrossDAO import MovingAverageCrossDAO
from MovingAverageCrossStrategy import MovingAverageCrossStrategy


def verify_dates(start_date, end_date):
    #TODO: add functionality and throw exception if tickers dont have data for dates
    print "need to implement"


def run_strategy():
    global list_of_securities
    list_of_securities = []
    for ticker in tickers:
        print "\nProcessing ticker: " + str(ticker[1])
        bars = ma_dao.read_data(ticker[1], '1995-10-25', '2005-10-27')
        bars.set_index(bars["price_date"], drop=True, append=False, inplace=True, verify_integrity=False)
        print "bar is:"
        print bars['close_price']
        symbol = ticker[1]
        mac = MovingAverageCrossStrategy(symbol, bars, short_window=100, long_window=400)
        signals = mac.generate_signals()
        mocs = MarketOnCloseSecurity(symbol, bars, signals)
        list_of_securities.append(mocs)


if __name__ == "__main__":
    ma_dao = MovingAverageCrossDAO("host", "user", "password", "databases name")

    #Before we get tickers, need to decide on dates to run the strategy over. Next we need to verify the companies
    #running the algo actually have data for that date
    start = '2000-02-01'
    end = '2016-02-03'

    verify_dates(start, end)

    # Get universe of stocks
    tickers = ma_dao.read_tickers()

    # Run strategy on universe
    run_strategy()

    # Generate portfolio
    portfolio = MarketOnClosePortfolio(list_of_securities, initial_capital=100000.0)

    # Run backtest on portfolio
    returns = portfolio.backtest_portfolio()

    # Show results
    plot = Plotter(portfolio, returns)
    plot.plot_price_with_signals()
    #plot.plot_equity_curve()
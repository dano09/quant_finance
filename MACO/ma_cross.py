#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
from MarketOnClosePortfolio import MarketOnClosePortfolio
from MarketOnCloseSecurity import MarketOnCloseSecurity
from MovingAverageCrossDAO import MovingAverageCrossDAO
from MovingAverageCrossStrategy import MovingAverageCrossStrategy
from PlotStrategy import PlotStrategy
from PlotPortfolio import PlotPortfolio
import traceback
import pandas as pd
import sys
import random


def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')


def run_strategy(start_date, end_date, universe, s_mavg, l_mavg):
    list_of_securities = []
    for ticker in universe:
        print "\nProcessing ticker: " + str(ticker)
        bars = ma_dao.read_data(ticker, start_date, end_date)
        bars.set_index(bars["price_date"], drop=True, append=False, inplace=True, verify_integrity=False)
        mac = MovingAverageCrossStrategy(ticker, bars, short_window=s_mavg, long_window=l_mavg)
        signals = mac.generate_signals()
        mocs = MarketOnCloseSecurity(ticker, bars, signals)
        list_of_securities.append(mocs)

    return list_of_securities


def calculate_avg_volume(bars):
    try:
        avg_volume = bars['volume']
    except Exception as e:
        print "E: " + str(e)
        print(traceback.format_exception(*sys.exc_info()))
        raise

    length = bars.shape
    total_vol = avg_volume.cumsum()
    max = total_vol.max()

    return max / length[0]


def get_universe_by_market_caps(start, end):
    tickers = ma_dao.get_universe(start, end)
    volume_df = pd.DataFrame(index=tickers)
    volume_df['volume'] = 0
    print_full(volume_df)
    for ticker in tickers:
        bars = ma_dao.read_data(ticker, start, end)
        universe.append(bars)
        try:
            volume = calculate_avg_volume(bars)
            volume_df.set_value(ticker, 'volume', volume)

        except Exception as e:
            print "Ticker : " + str(ticker) + " did not have data!"
            print "E: " + str(e)
            print(traceback.format_exception(*sys.exc_info()))


    # To handle liquidity concerns, only consider smaller cap stocks with an average volume of at least 200,000
    volume_df = volume_df[volume_df.volume > 200000]

    sorted_df = volume_df.sort_values('volume', axis=0)
    low_cap = sorted_df.head(4).index.values
    high_cap = sorted_df.tail(4).index.values
    print "sorted_df"
    print_full(sorted_df)
    return low_cap, high_cap;


def perform_backtesting(universe, capital, s_mavg, l_mavg):
    # Run strategy on universe of securities
    try:
        list_of_securities = run_strategy(start, end, universe, s_mavg, l_mavg)
    except ValueError as e:
        print "Error: " + str(e)

    # Generate portfolio
    portfolio = MarketOnClosePortfolio(list_of_securities, initial_capital=capital)
    # Run backtest on portfolio
    backtested_portfolio = portfolio.backtest_portfolio()
    # Plot Strategies
    for security in list_of_securities:
        plot_strat = PlotStrategy(security)
        plot_strat.plot_price_with_signals()
    # Plot portfolio
    plot_portfolio = PlotPortfolio(portfolio, backtested_portfolio)
    trades = plot_portfolio.plot_equity_curve(start, end)

    return trades, backtested_portfolio['total'][-1]



if __name__ == "__main__":
    universe = []
    ma_dao = MovingAverageCrossDAO("localhost", "root", "GoldfishSmiles.com", "securities_master")

    # Pick dates for backtesting
    # Parameters for Algorithm
    start = '1998-02-01'
    end = '2016-10-01'
    capital = 100000
    s_mavg = 100
    l_mavg = 200

    parameters = [start, end, s_mavg, l_mavg, capital]
    # Test can be ran on a random set of companies or a set of large and small companies
    choose_random = True

    # Limit universe to stocks within backtest history
    tickers = ma_dao.get_universe(start, end)

    if choose_random:
        # Universe option: Random selection
        for i in range(4):
            universe.append(random.choice(tickers))

        meta_data = list(universe)
        meta_data.extend(parameters)

        num_of_trades, closing_capital = perform_backtesting(universe, capital, s_mavg, l_mavg)
        backtest_results = ['random', num_of_trades, closing_capital]
        meta_data.extend(backtest_results)

        #ma_dao.write_data(meta_data)

    else:
        # Universe derived by small and large companies
        universe = get_universe_by_market_caps(start, end)

        # Test Small Caps
        meta_data = universe[0]
        meta_data.extend(parameters)

        num_of_trades, closing_capital = perform_backtesting(universe[0], capital, s_mavg, l_mavg)
        backtest_results = ['small_cap', num_of_trades, closing_capital]
        meta_data.extend(backtest_results)

        #ma_dao.write_data(meta_data)

        # Test Large Caps
        meta_data = universe[1]
        meta_data.extend(parameters)

        num_of_trades, closing_capital = perform_backtesting(universe[1], capital, s_mavg, l_mavg)
        backtest_results = ['large_cap', num_of_trades, closing_capital]
        meta_data.extend(backtest_results)

        #ma_dao.write_data(meta_data)



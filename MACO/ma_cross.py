#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
import sys
import time
import traceback

import pandas as pd

from MACO.dao.MovingAverageCrossDAO import MovingAverageCrossDAO
from MACO.maco_display.PlotStrategy import PlotStrategy
from MACO.maco_model.EventGenerator import EventGenerator
from MACO.maco_model.MarketOnClosePortfolio import MarketOnClosePortfolio
from MACO.maco_model.MarketOnCloseSecurity import MarketOnCloseSecurity
from MACO.maco_model.MovingAverageCrossStrategy import MovingAverageCrossStrategy


def run_strategy(start_date, end_date, universe, s_mavg, l_mavg):
    """

    :param start_date:
    :param end_date:
    :param universe:
    :param s_mavg:
    :param l_mavg:
    :return:
    """

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
        length = bars.shape
        total_vol = avg_volume.cumsum().max()
    except Exception as e:
        print "E: " + str(e)
        print(traceback.format_exception(*sys.exc_info()))
        raise

    return total_vol / length[0]


def get_universe_by_market_caps(start, end, calculate_flag):
    """
    Tickers are sorted by volume in database. If first time being ran,
    calculate_flag should be set to true to perform the calculation.
    Otherwise just retrieve entries from the database.
    :param start:
    :param end:
    :param calculate_flag: Used to calculate average volume.
    :return:
    """
    # Calculate average volume for each ticker. Results are saved in the
    # database for performance.
    if calculate_flag:
        tickers = ma_dao.get_universe(start, end)
        volume_df = pd.DataFrame(index=tickers)
        volume_df['volume'] = 0

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
        #TODO: Change variable names
        volume_df = volume_df[volume_df.volume > 200000]
        sorted_df = volume_df.sort_values('volume', axis=0)
        sorted_df['ticker'] = sorted_df.index
        # Remove any tickers that could represent secondary class shares. (E.G. BF-B)
        clean_df = sorted_df[~sorted_df['ticker'].str.contains("-")]

        ma_dao.save_universe_by_volume(clean_df)

    universe_by_volume = ma_dao.read_universe_by_volume()

    df_length = universe_by_volume.shape
    total = df_length[0]
    half = total / 2

    low_cap = universe_by_volume.head(half)['ticker'].values
    high_cap = universe_by_volume.tail(half)['ticker'].values

    return low_cap, high_cap;


def perform_maco(universe, dates, mavg_windows, capital):
    try:
        # Run strategy on universe of securities
        list_of_securities = run_strategy(dates[0], dates[1], universe, mavg_windows[0], mavg_windows[1])

        # Generate portfolio of signals from the MACO strategy
        signal_portfolio = MarketOnClosePortfolio(list_of_securities, initial_capital=capital)

        # Run backtest on portfolio
        backtest_portfolio = signal_portfolio.backtest_portfolio()

        # Get number of trades for meta_data
        event_gen = EventGenerator(signal_portfolio, backtest_portfolio)
        trade_count = event_gen.get_trade_count()

        # Plot Strategies
        for security in list_of_securities:
            plot_strat = PlotStrategy(security)
            plot_strat.plot_price_with_signals()
        # Plot portfolio
        #plot_portfolio = PlotPortfolio(portfolio, backtest_results)
        #trades = plot_portfolio.plot_equity_curve(start, end)

    except ValueError as e:
        print "Error: " + str(e)
        raise

    return signal_portfolio, backtest_portfolio, trade_count

def generate_parameters(stock_universe):
    #TODO: Determine # of shares to buy/sell in here
    start_capital = 100000

    # Define the small and large lookback windows. These are what determine
    # the moving averages, which determines the signals for the strategy
    #windows = (180, 400), (275, 350), (340, 375)
    windows = (275, 350)

    #Get smallest 4 companies by volume
    print stock_universe
    small_caps = stock_universe[0][:4]

    #Get largest 4 companies by volume
    large_caps = stock_universe[1][-4:]

    return windows, small_caps, large_caps, start_capital


def run_maco(maco_params):

        # Identify parameters
        dates = maco_params[0], maco_params[1]
        lookback_windows = maco_params[2]
        tickers = maco_params[3]
        capital = maco_params[4]
        universe_type = maco_params[5]

        # Collect metadata on the strategy implemented
        meta_data = [tickers[0], tickers[1], tickers[2], tickers[3],
                     dates[0], dates[1],
                     lookback_windows[0], lookback_windows[1],
                     capital,
                     universe_type]

        try:
            # Market on Close Portfolio (MOCP)
            mocp, backtest_portfolio, num_of_trades = perform_maco(tickers, dates, lookback_windows, capital)
            backtest_results = [num_of_trades, backtest_portfolio['total'][-1]]
            meta_data.extend(backtest_results)

            # Save meta data and parameters of MACO strategy
            row_id = ma_dao.write_data(meta_data)

            # Save signals generated for each security
            for ticker_id, security in enumerate(mocp.market_on_close_securities):
                ma_dao.save_signals(security.signals, security.symbol, row_id)

            # Save backtest results
            ma_dao.save_maco_backtest(backtest_portfolio, row_id)

        except Exception as e:
            print "Could not complete MACO for start date: " + str(dates[0]) + " and end date: " + str(dates[1]) + \
                  " with lookback periods of: " + str(lookback_windows[0]) + " and: " + str(lookback_windows[1]) + \
                  " for the following companies:  " + str(tickers)

            print "E: " + str(e)
            print(traceback.format_exception(*sys.exc_info()))


def validate_dates(start_date, end_date):
    """
    Start and end date must be a business day containing price data or graphs will not work correctly
    :param start_date:
    :param end_date:
    :return:
    """
    valid_dates_flag = True

    start_data = ma_dao.validate_date(start_date)
    end_data = ma_dao.validate_date(end_date)

    if len(start_data) == 0 or len(end_data) == 0:
        valid_dates_flag = False

    return valid_dates_flag

if __name__ == "__main__":
    start_time = time.time()
    universe = []
    ma_dao = MovingAverageCrossDAO("localhost", "root", "GoldfishSmiles.com", "securities_master")
    start = '1998-01-02'
    end = '2016-10-14'

    valid_test_flag = validate_dates(start, end)
    assert (valid_test_flag is True), "Must have valid price dates!"

    # First time running requires flag to be true to sort tickers by volume traded.
    # After first run we simply retrieve sorted tickers from database and can set
    # flag to false
    calculate_flag = False

    # Limit universe to stocks within backtest history
    tickers = ma_dao.get_universe(start, end)

    universe = get_universe_by_market_caps(start, end, calculate_flag)

    # Define parameters for backtest
    params = generate_parameters(universe)

    small_cap_params = start, end, params[0], params[1], params[3], 'small_cap'
    large_cap_params = start, end, params[0], params[2], params[3], 'large_cap'

    # Test Small Caps
    run_maco(small_cap_params)

    # Test Large Caps
    run_maco(large_cap_params)


    print("Time to complete:         %s seconds" % round((time.time() - start_time), 4))



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


def run_strategy(start_date, end_date, universe, s_mavg, l_mavg, trade_amount, analysis_flag):
    """
    Perform the Moving Average Crossover on each company in the universe
    :param start_date: datetime - Start of Strategy
    :param end_date: datetime - End of Strategy
    :param universe: list (string) - ticker for each company
    :param s_mavg: int - shorter moving average window
    :param l_mavg: int - longer moving average window
    :param trade_amount: int - Number of Shares to buy or sell
    :param analysis_flag: boolean - True = Analysis on Portfolio, False = Portfolio creation
    :return: list (MarketOnCloseSecurities) - signals generated from MACO
    """
    list_of_securities = []

    if analysis_flag:
        # Creating portfolios with one ticker. This way we can compare low-volume and high-volume companies
        print "\nProcessing ticker: " + str(universe)
        # Get price data
        bars = ma_dao.read_data(universe, start_date, end_date)
        bars.set_index(bars["price_date"], drop=True, append=False, inplace=True, verify_integrity=False)

        # Create the Strategy
        mac = MovingAverageCrossStrategy(universe, bars, short_window=s_mavg, long_window=l_mavg)

        # Generate signals from the strategy
        signals = mac.generate_signals()

        # Encapsulate the price data, signals, and company in a MarketOnCloseSecurity object
        mocs = MarketOnCloseSecurity(universe, bars, signals)
        list_of_securities.append(mocs)
    else:
        # General case for portfolio case on a set of tickers
        for ticker in universe:
            print "\nProcessing ticker: " + str(ticker)
            # Get price data
            bars = ma_dao.read_data(ticker, start_date, end_date)
            bars.set_index(bars["price_date"], drop=True, append=False, inplace=True, verify_integrity=False)

            # Create the Strategy
            mac = MovingAverageCrossStrategy(ticker, bars, short_window=s_mavg, long_window=l_mavg)

            # Generate signals from the strategy
            signals = mac.generate_signals()

            # Encapsulate the price data, signals, and company in a MarketOnCloseSecurity object
            mocs = MarketOnCloseSecurity(ticker, bars, signals)
            list_of_securities.append(mocs)

    return list_of_securities


def calculate_avg_volume(bars):
    """
    :param bars: dataframe - OHLCAV data for a company
    :return: double - Average volume
    """
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
    :param start: Datetime
    :param end: Datetime
    :param calculate_flag: boolean - Used to calculate average volume.
    :return: tuple - low volume tickers and high volume tickers
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
        volume_df = volume_df[volume_df.volume > 200000]
        sorted_df = volume_df.sort_values('volume', axis=0)
        sorted_df['ticker'] = sorted_df.index

        # Remove any tickers that could represent secondary class shares. (E.G. BF-B)
        clean_df = sorted_df[~sorted_df['ticker'].str.contains("-")]

        ma_dao.save_universe_by_volume(clean_df)

    # Retrieve tickers by volume from the database
    universe_by_volume = ma_dao.read_universe_by_volume()

    df_length = universe_by_volume.shape
    total = df_length[0]
    half = total / 2

    # Split universe by high and low volume
    low_cap = universe_by_volume.head(half)['ticker'].values
    high_cap = universe_by_volume.tail(half)['ticker'].values

    return low_cap, high_cap


def perform_maco(universe, dates, mavg_windows, capital, trade_amount, analysis_flag):
    """
    1. Runs the MACO Strategy for each Security and generates the MOCP portfolio.
    2. Runs backtest on MOCP portfolio
    3. Generates total number of trades for analysis
    :param universe: list - Companies that make up the portfolio
    :param dates: tuple (datetimes) - Start and end date to run strategy over
    :param mavg_windows: tuple (ints) - Defines how the MACO generates signals
    :param capital: int - Starting capital for the portfolio
    :param trade_amount: int - Number of shares to buy or sell in MACO
    :param analysis_flag: boolean - Either doing analysis or creating portfolio
    :return:
        1. dataframe - Portfolio of the companies and their signals to generate trades
        2. dataframe - Resulting backtested portfolio
        3. int - number of trades executed during backtest
    """
    try:
        # Run strategy on universe of securities
        list_of_securities = run_strategy(dates[0], dates[1],
                                          universe,
                                          mavg_windows[0], mavg_windows[1],
                                          trade_amount,
                                          analysis_flag
                                          )

        # Generate portfolio of signals from the MACO strategy
        signal_portfolio = MarketOnClosePortfolio(list_of_securities, trade_amount, initial_capital=capital)

        # Run backtest on portfolio
        backtest_portfolio = signal_portfolio.backtest_portfolio()

        # Get number of trades for meta_data
        event_gen = EventGenerator(signal_portfolio, backtest_portfolio)
        trade_count = event_gen.get_trade_count()

    except ValueError as e:
        print "Error: " + str(e)
        raise

    return signal_portfolio, backtest_portfolio, trade_count


def generate_parameters(stock_universe, analysis_flag):
    """
    Creates the parameters used in the MACO strategy
    :param stock_universe: tuple
    :return: tuple - MACO parameters
    """
    start_capital = 100000

    trade_quantity = 100
    # Define the small and large lookback windows. These are what determine
    # the moving averages, which determines the signals for the strategy
    windows = (30, 120)

    if analysis_flag:
        # Get entire universe for both low and high volume companies
        small_vol_universe = stock_universe[0]
        large_vol_universe = stock_universe[1]

    else:
        # Create two portfolios, each containing 4 companies
        small_vol_universe = stock_universe[0][:4]
        large_vol_universe = stock_universe[1][-4:]

    return windows, small_vol_universe, large_vol_universe, start_capital, trade_quantity


def setup_and_run_maco(maco_params, analysis_flag):
    """
    Set up parameters and perform the Moving Average Crossover. Save the meta-data,
    signal generations, and backtesting results to the database
    :param maco_params: list - initial parameters to run the MACO strategy
    """
    # Identify parameters
    dates = maco_params[0], maco_params[1]
    lookback_windows = maco_params[2]
    tickers = maco_params[3]
    capital = maco_params[4]
    universe_type = maco_params[5]
    trade_amount = maco_params[6]

    # Collect metadata on the strategy implemented
    if analysis_flag:
        meta_data = [tickers,
                     dates[0], dates[1],
                     lookback_windows[0], lookback_windows[1],
                     capital,
                     universe_type]
    else:
        meta_data = [tickers[0], tickers[1], tickers[2], tickers[3],
                dates[0], dates[1],
                lookback_windows[0], lookback_windows[1],
                capital,
                universe_type]

    try:
        # Market on Close Portfolio (MOCP) contains the initial data for backtesting
        # while the backtest_portfolio contains the results of the backtest
        mocp, backtest_portfolio, num_of_trades = perform_maco(
            tickers,
            dates,
            lookback_windows,
            capital,
            trade_amount,
            analysis_flag)

        backtest_results = [num_of_trades, backtest_portfolio['total'][-1]]
        meta_data.extend(backtest_results)

        # Save meta data and parameters of MACO strategy
        row_id = ma_dao.write_data(meta_data, analysis_flag)

        # Save signals generated for each security
        for ticker_id, security in enumerate(mocp.market_on_close_securities):
            ma_dao.save_signals(security.signals, security.symbol, row_id)

        # Save backtest results
        ma_dao.save_maco_backtest(backtest_portfolio, row_id, analysis_flag)

    except Exception as e:
        print "Could not complete MACO for start date: " + str(dates[0]) + " and end date: " + str(dates[1]) + \
                " with lookback periods of: " + str(lookback_windows[0]) + " and: " + str(lookback_windows[1]) + \
                " for the following companies:  " + str(tickers)

        print "E: " + str(e)
        print(traceback.format_exception(*sys.exc_info()))


def validate_dates(start_date, end_date):
    """
    Start and end date must be a business day containing price data or graphs will not work correctly
    """
    valid_dates_flag = True

    start_data = ma_dao.validate_date(start_date)
    end_data = ma_dao.validate_date(end_date)

    if len(start_data) == 0 or len(end_data) == 0:
        valid_dates_flag = False

    return valid_dates_flag


def volume_comparison_run(maco_params):
    """
    This method performs MACO on several low and high volume companies
    to try and identify which is more profitable for the MACO strategy
    :param maco_params:
    :return:
    """
    small_vol_universe = maco_params[1]
    large_vol_universe = maco_params[2]

    for company in small_vol_universe:
        small_cap_params = start, end, params[0], company, params[3], 'small_vol', params[4]
        setup_and_run_maco(small_cap_params, True)

    for company in large_vol_universe:
        large_cap_params = start, end, params[0], company, params[3], 'large_vol', params[4]
        setup_and_run_maco(large_cap_params, True)

if __name__ == "__main__":
    start_time = time.time()
    ma_dao = MovingAverageCrossDAO("localhost", "root", "GoldfishSmiles.com", "securities_master")
    start = '1998-01-02'
    end = '2016-10-14'

    valid_test_flag = validate_dates(start, end)
    assert (valid_test_flag is True), "Must have valid price dates!"

    # First time running requires flag to be true to sort tickers by volume traded.
    # After first run we simply retrieve sorted tickers from database and can set
    # flag to false
    calculate_flag = False

    # For comparing returns of low and high volume portfolios.
    # Does not actually create a portfolio when set to True
    analysis_flag = True

    universe = get_universe_by_market_caps(start, end, calculate_flag)

    # Define parameters for backtest
    params = generate_parameters(universe, analysis_flag)

    if analysis_flag:
        # Do an aggregate comparison of high vs low volume companies
        volume_comparison_run(params)
    else:
        # Generate Portfolio and test MACO
        small_cap_params = start, end, params[0], params[1], params[3], 'small_vol', params[4]
        large_cap_params = start, end, params[0], params[2], params[3], 'large_vol', params[4]

        # Test Small Caps
        setup_and_run_maco(small_cap_params, analysis_flag)

        # Test Large Caps
        setup_and_run_maco(large_cap_params, analysis_flag)


    print("Time to complete:         %s seconds" % round((time.time() - start_time), 4))



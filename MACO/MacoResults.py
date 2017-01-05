#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 12/04/2016

"""
import time

from MACO.maco_display.PlotVolumeAnalysis import PlotVolumeAnalysis
from MACO.maco_model.MarketOnCloseSecurity import MarketOnCloseSecurity
from MACO.dao.MACO_DAO import MACO_DAO
from MACO.maco_display.PlotPortfolio import PlotPortfolio
from MACO.maco_display.PlotResults import PlotResults
from MACO.maco_display.PlotStrategy import PlotStrategy
from MACO.maco_model.EventGenerator import EventGenerator
from MACO.maco_model.MarketOnClosePortfolio import MarketOnClosePortfolio


def generate_mocs(tickers, maco_id, start, end):
    """Generates MarketOnCloseSecurity objects"""
    securities = []
    for ticker in tickers:
        if ticker:
            signal_data = ma_dao.read_maco_signals(maco_id, ticker)
            signal_data.set_index(signal_data['price_date'], drop=True, inplace=True)
            bars = ma_dao.read_data(ticker, start, end)
            bars.set_index(bars["price_date"], drop=True, inplace=True, )
            mocs = MarketOnCloseSecurity(ticker, bars, signal_data)
            securities.append(mocs)

    return securities

def setup_portfolio(maco_meta):
    # Get MACO id
    maco_id = maco_meta['id'].values[0]

    # Retrieve MACO backtest from database
    maco_backtest = ma_dao.read_maco_backtest(maco_id)
    maco_backtest.set_index(maco_backtest['price_date'], drop=True, inplace=True)

    start_date = str(maco_backtest.first_valid_index())
    end_date = str(maco_backtest.last_valid_index())

    # Get tickers
    tickers = maco_meta['ticker_1'].values[0], maco_meta['ticker_2'].values[0], \
              maco_meta['ticker_3'].values[0], maco_meta['ticker_4'].values[0],

    mocs = generate_mocs(tickers, maco_id, start_date, end_date)
    signal_portfolio = MarketOnClosePortfolio(mocs)

    # Setup events for table in portfolio graph
    eg = EventGenerator(signal_portfolio, maco_backtest)
    events, event_dates = eg.generate_events(start_date, end_date)
    num_of_trades = eg.get_trade_count()

    plotter = PlotPortfolio(signal_portfolio, maco_backtest, events, event_dates, num_of_trades)

    return signal_portfolio, plotter, maco_backtest


def display_maco_signals(securities):
    """Display signals generated from MACO"""
    for security in securities:
        plot_strat = PlotStrategy(security)
        plot_strat.plot_large_number_of_signals()
        #plot_strat.plot_price_with_signals()


def setup_analysis(maco_meta, quantity=None):
    # Get MACO id
    backtests = []
    maco_ids = maco_meta['id'].values

    if quantity:

        if maco_meta['universe_type'][0] == 'small_vol':
            maco_ids = maco_ids[:quantity]
        else:
            maco_ids = maco_ids[-quantity:]

    for maco_id in maco_ids:
        # Retrieve MACO backtest from database
        maco_backtest = ma_dao.read_maco_backtest(maco_id)
        maco_backtest.set_index(maco_backtest['price_date'], drop=True, inplace=True)
        backtests.append(maco_backtest)

    return backtests


if __name__ == "__main__":
    start_time = time.time()
    ma_dao = MACO_DAO("localhost", "root", "GoldfishSmiles.com", "securities_master")
    analysis_flag = False
    s_window = 14
    l_window = 30

    small_vol_meta = ma_dao.read_maco_meta('small_vol', s_window, l_window)
    large_vol_meta = ma_dao.read_maco_meta('large_vol', s_window, l_window)

    if analysis_flag:
        s_backtests = setup_analysis(small_vol_meta)
        l_backtests = setup_analysis(large_vol_meta)
        pva = PlotVolumeAnalysis(s_backtests, l_backtests)
        pva.plot_results()

    else:
        mocp_small, plotter_small, backtest_small = setup_portfolio(small_vol_meta)
        #mocp_large, plotter_large, backtest_large = setup_portfolio(large_vol_meta)
        """
        PART 1:
        Display results for small-volume portfolio
        """
        # Display signals generated for each small cap company
        display_maco_signals(mocp_small.market_on_close_securities)

        if plotter_small.trades > 20:
            # Display portfolio and events on two different figures
            plotter_small.plot_large_equity_curve()
        else:
            # Display portfolio and events on same figure
            plotter_small.plot_equity_curve()

        """
        PART 2:
        Display results for small-large portfolio
        """
        # Display signals generated for each small cap company
        display_maco_signals(mocp_large.market_on_close_securities)

        if plotter_large.trades > 20:
            # Display portfolio and events on two different figures
            plotter_large.plot_large_equity_curve()
        else:
            # Display portfolio and events on same figure
            plotter_large.plot_equity_curve()

        """
        PART 3:
        Display and compare small-volume and large-volume performance
        """
        trades = plotter_small.trades, plotter_large.trades
        pr = PlotResults(backtest_small, backtest_large, trades)
        pr.plot_results()

    print("Time to complete:         %s seconds" % round((time.time() - start_time), 4))
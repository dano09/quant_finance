from MarketOnCloseSecurity import MarketOnCloseSecurity

from MACO.dao.MovingAverageCrossDAO import MovingAverageCrossDAO
from MACO.maco_display.PlotPortfolio import PlotPortfolio
from MACO.maco_display.PlotResults import PlotResults
from MACO.maco_display.PlotStrategy import PlotStrategy
from MACO.maco_model.EventGenerator import EventGenerator
from MACO.maco_model.MarketOnClosePortfolio import MarketOnClosePortfolio


def generate_mocs(tickers, maco_id, start, end):
    """Generates MarketOnCloseSecurity objects"""
    securities = []
    for ticker in tickers:
        signal_data = ma_dao.read_maco_signals(maco_id, ticker)
        signal_data.set_index(signal_data['price_date'], drop=True, inplace=True)
        bars = ma_dao.read_data(ticker, start, end)
        bars.set_index(bars["price_date"], drop=True, inplace=True, )
        mocs = MarketOnCloseSecurity(ticker, bars, signal_data)
        securities.append(mocs)

    return securities

def setup_for_graphs(maco_meta):
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
        plot_strat.plot_price_with_signals()

if __name__ == "__main__":
    ma_dao = MovingAverageCrossDAO("localhost", "root", "GoldfishSmiles.com", "securities_master")

    # Display results for small-cap portfolio
    small_cap_meta = ma_dao.read_maco_meta('small_cap')

    mocp_small, plotter_small, backtest_small = setup_for_graphs(small_cap_meta)

    # Display signals generated for each small cap company
    display_maco_signals(mocp_small.market_on_close_securities)


    if plotter_small.trades > 20:
        print ""
        plotter_small.plot_large_equity_curve()
    else:
        # Display portfolio and events
        plotter_small.plot_equity_curve()


    # Display results for large-cap portfolio
    large_cap_meta = ma_dao.read_maco_meta('large_cap')


    mocp_large, plotter_large, backtest_large = setup_for_graphs(large_cap_meta)

    # Display signals generated for each small cap company
    #display_maco_signals(mocp_large.market_on_close_securities)

    if plotter_large.trades > 20:
        print ""
        #plotter_large.plot_large_equity_curve()
    else:
        # Display portfolio and events
        plotter_large.plot_equity_curve()



    trades = plotter_small.trades, plotter_large.trades
    pr = PlotResults(backtest_small, backtest_large, trades)
    pr.plot_results()
    print "done"
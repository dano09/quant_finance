import pandas as pd
import MySQLdb as mdb
import datetime


def get_db_connection():
    """
    Utility method that provides database credentials
    :return: MySQL Server database connection
    """
    db_host = 'localhost'
    db_user = 'root'
    db_pass = 'GoldfishSmiles.com'
    db_name = 'securities_master'
    return mdb.connect(db_host, db_user, db_pass, db_name)


def retrieve_db_tickers(connection):
    """
    Retrieve ticker symbols for each company that are not delisted
    :param connection: Database connection
    :return: List of all tickers from database
    """
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT id, ticker FROM symbol where status_id = 2")
        data = cur.fetchall()
        return [(d[0], d[1]) for d in data]


def retrieve_one_ticker(connection):
    """
    Retrieve one ticker for testing
    :param connection: Database connection
    :return: List of all tickers from database
    """
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT id, ticker FROM symbol where id = 1")
        data = cur.fetchall()
        return [(d[0], d[1]) for d in data]


def retrieve_price_data(con, ticker, vendor_id, start, end):
    """
    Retrieve price data from the database for the specific
    ticker over the specified range.
    :param con: Database connection
    :param ticker: String - The company's ticker symbol
    :param vendor_id: Int - The vendor we grab the price data from
    :param start: Date -We grab data starting at this date
    :param end: Date - The data ends at this date
    :return:Dataframe of all the price data
    """
    with con:
        cur = con.cursor()
        # First query is to retrieve the id for the given symbol
        cur.execute("SELECT id FROM symbol WHERE ticker = %s", [ticker])
        ticker_id = cur.fetchall()
        ticker_id = ticker_id[0][0]
        # Second query gathers OHLCAV data
        cur.execute("SELECT * FROM daily_price "
                    "WHERE symbol_id = %s AND data_vendor_id = %s "
                    "AND price_date BETWEEN %s AND %s", (ticker_id, vendor_id, start, end))

        # Return none if no data exists for the ticker within the specified
        # time frame, otherwise return a dataframe with the OHLCAV data
        if not cur.rowcount:
            if vendor_id == 1:
                print "Yahoo had no price data available for " + str(start)
            else:
                print "Quandl had no price data available for " + str(start)
            price_data = None
        else:
            price_data = pd.DataFrame(list(cur.fetchall()))
            price_data.columns = ['id', 'symbol_id', 'vendor_id', 'price_date', 'created_date',
                                  'last_updated_date', 'open_price', 'high_price', 'low_price', 'close_price',
                                  'adj_close_price', 'volume']

        return price_data


def retrieve_data_with_zeros(con, ticker, start, end):
    """
    Retrieve data that has been cross-referenced and given zeros for any inconsistent values. The
    data used from this query will be interpolated to fill those zero values.
    :param con: Database connection
    :param ticker: String - The company's ticker symbol
    :param start: Date - We grab data starting at this date
    :param end: Date - The data ends at this date
    :return: Dataframe - Data that needs to be interpolated
    """
    with con:
        cur = con.cursor()
        # First query is to retrieve the id for the given symbol
        cur.execute("SELECT id FROM symbol WHERE ticker = %s", [ticker])
        ticker_id = cur.fetchall()
        ticker_id = ticker_id[0][0]

        # Second query gathers OHLCAV data
        cur.execute("SELECT * FROM clean_price "
                    "WHERE symbol_id = %s AND price_date >= %s AND price_date <= %s", (ticker_id, start, end))

        # Return none if no data exists for the ticker within the specified
        # time frame, otherwise return a dataframe with the OHLCAV data
        if not cur.rowcount:
            print "No price data available for " + ticker + " on " + str(start)
            price_data = None
        else:
            price_data = pd.DataFrame(list(cur.fetchall()))
            price_data.columns = ['id', 'symbol_id', 'price_date', 'created_date',
                                  'last_updated_date', 'open_price', 'high_price', 'low_price', 'close_price',
                                  'adj_close_price', 'volume']

        return price_data


def retrieve_clean_data(con, ticker, start, end):
    """
    Currently same as retrieve_data_with_zeros, but will be modified to collect from a different table in the future
    :param con: Database connection
    :param ticker: String - The company's ticker symbol
    :param start:  Date - We grab data starting at this date
    :param end: Date - The data ends at this date
    :return:
    """
    with con:
        cur = con.cursor()
        # First query is to retrieve the id for the given symbol
        cur.execute("SELECT id FROM symbol WHERE ticker = %s", [ticker])
        ticker_id = cur.fetchall()
        ticker_id = ticker_id[0][0]

        # Second query gathers OHLCAV data
        cur.execute("SELECT * FROM cleaned_price "
                    "WHERE symbol_id = %s AND price_date >= %s AND price_date <= %s", (ticker_id, start, end))

        # Return none if no data exists for the ticker within the specified
        # time frame, otherwise return a dataframe with the OHLCAV data
        if not cur.rowcount:
            print "No price data available for " + ticker + " on " + str(start)
            price_data = None
        else:
            price_data = pd.DataFrame(list(cur.fetchall()))
            price_data.columns = ['id', 'symbol_id', 'price_date', 'created_date',
                                  'last_updated_date', 'open_price', 'high_price', 'low_price', 'close_price',
                                  'adj_close_price', 'volume']

        return price_data


def insert_data_into_db(con, data_vendor_id, symbol_id, daily_data):
    """
    Takes the OHLCAV data for a specific company, over pre-defined
    time range and adds it to the Database.
    :param con: Database connection
    :param data_vendor_id: Int used to identify the vendor
    :param symbol_id: Int used to identify the company
    :param daily_data: List of Tuples containing price data
    """
    timestamp = datetime.datetime.utcnow()
    # Map daily price data to the columns of our database table
    daily_data = [[data_vendor_id, symbol_id, d[0], timestamp, timestamp,
    d[1], d[2], d[3], d[4], d[5], d[6]] for d in daily_data]

    # Build the parametrized query string
    column_str = """data_vendor_id, symbol_id, price_date, created_date,
          last_updated_date, open_price, high_price, low_price,
          close_price, adj_close_price, volume"""
    insert_str = ("%s, " * 11)[:-2]
    query_string = "INSERT INTO daily_price (%s) VALUES (%s)" % (column_str, insert_str)

    # Connect with MySQL database and perform the insert query
    with con:
        cur = con.cursor()
        cur.executemany(query_string, daily_data)


def insert_clean_data_into_db(con, price_data):
    """
    Insert cross-referenced dataframe into the database. Used by the cleanPricingData script
    :param con: Database connection
    :param price_data: Dataframe - OHLCAV data after being cross-validated between the two vendors
    """
    with con:
        price_data.to_sql(con=con, name='clean_price', if_exists='append', index=False, flavor='mysql')


def insert_clean_and_interpolated_data_into_db(con, price_data):
    """
    Insert cross-referenced, and Interpolated dataframe into the database. Used by the fillZeros script.
    :param con: Database connection
    :param price_data: Dataframe - OHLCAV data after being cross-validated and having its zeros filled
    """
    with con:
        price_data.to_sql(con=con, name='cleaned_price', if_exists='append', index=False, flavor='mysql')


def assign_starting_date(con, ticker, first_day):
    """
    Used via obtainYahooPriceData script to set the first day the database started collecting price data for a
    specific company. This can either be the start of the historical data collection, January 1st, 1998,
    or the companies IPO.
    :param con: Database connection
    :param ticker: String - The company's ticker symbol
    :param first_day: Date - We grab data starting at this date
    """
    query = """ UPDATE symbol SET first_price_date = %s WHERE ticker = %s """
    data = (first_day, ticker)
    with con:
        cur = con.cursor()
        cur.execute(query, data)


def update_symbols(con, ticker, final_day):
    """
    Used by delistStocks script to update tickers that are delisted.
    :param con: Database connection
    :param ticker: String - The company's ticker symbol
    :param final_day: Date - The last day the ticker was listed publicly
    """
    date_query = """ UPDATE symbol SET last_price_date = %s WHERE ticker = %s """
    date_data = (final_day, ticker)

    status_query = """ UPDATE symbol SET status_id = %s WHERE ticker = %s """
    status_data = (3, ticker)
    with con:
        cur = con.cursor()
        cur.execute(date_query, date_data)
        cur.execute(status_query, status_data)

def get_universe_by_market_caps(start, end):
    """
    Used to determine market cap of companies over time-series
    :param start:
    :param end:
    :return:
    """
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

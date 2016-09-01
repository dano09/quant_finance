#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 8/10/2016
This script collects and saves QUANDL price data for
companies in the S&P500
"""
import quandl
import datetime
import MySQLdb as mdb
import sys
import os.path
from SharedFunctionsLib import *

timestamp = datetime.datetime.utcnow()
quandl.ApiConfig.api_key = '****'
failed_data_symbols = []

# Obtain a database connection to the MySQL instance
db_host = 'localhost'
db_user = 'root'
db_pass = '****'
db_name = '****'
con = mdb.connect(db_host, db_user, db_pass, db_name)

"""
TODO: REMOVE IF IMPORT WAS SUCCESSFUL
Retrive ticker symbols for each company from 
the database.

  returns - List of all tickers from database

def retrieve_db_tickers():
    with con:
        cur = con.cursor()
        cur.execute("SELECT id, ticker FROM symbol")
        data = cur.fetchall()
        return [(d[0], d[1]) for d in data]
"""
"""
Obtains price data from Quandl's API for the specificed company.
This function is currently set to get the most recent date, but is
capable of collecting all data within the specified start_date and
end_date parameters. The dates are in (YYYY, M, D) format

  ticker -  Ticker symbol that represents a company
  start - Collect pricing data starting at this date
  end - Collection of pricing data ends at this date
  returns - OHLCAV data for the company
"""
def get_Quandl_daily_data(ticker, start, end):
    prices = []
    symbol = format_ticker(ticker)
    valid_data_flag = True

    #Attempt to connect to Quandl API and retrieve price data
    try:
        data = quandl.get("WIKI/" + symbol, start_date=start, end_date=end)
    except Exception, e:
        print "Could not download QUANDL data: %s" % e
        valid_data_flag = False
        prices = -1
        failed_data_symbols.append(ticker)

    if valid_data_flag:
        # Map the dataframe into a list of tuples for easy
        # database insertion
        rows_of_data = [tuple(x) for x in data.to_records(index=True)]

        for row in rows_of_data:
            """Format data and set precision.
            The tuples entries are as follows:
            Date, Open, High, Low, Close, Adjusted Close, Volume
            """
            one_day_of_prices = (row[0],"%.4f" % row[1], "%.4f" % row[2],
            "%.4f" % row[3], "%.4f" % row[4], "%.4f" % row[11], row[5])
            prices.append(one_day_of_prices)

    return prices

"""
Takes the OHLCAV data for a specific company, over pre-defined
time range and adds it to the Database.

  data_vendor_id - Identification for Quandl
  symbol_id - What we use to relate the ticker and price data
  daily_data - List of tuples of the OHLCAV data
"""
def insert_data_into_db(data_vendor_id, symbol_id, daily_data):
    # Map daily price data to the columns of our database table
    daily_data = [(data_vendor_id, symbol_id, d[0], timestamp, timestamp,
    d[1], d[2], d[3], d[4], d[5], d[6]) for d in daily_data]

    # Build the paramaterized query string
    column_str = """data_vendor_id, symbol_id, price_date, created_date,
          last_updated_date, open_price, high_price, low_price,
          close_price, adj_close_price, volume"""
    insert_str = ("%s, " * 11)[:-2]
    query_string = "INSERT INTO daily_price2 (%s) VALUES (%s)" % (column_str, insert_str)

    #Connect with MySQL database and perform the insert query
    with con:
        cur = con.cursor()
        cur.executemany(query_string, daily_data)

"""
Utility: Creates file for failed tickers
"""
def generate_failure_file():
  save_path = '****'
  file_name = 'Failed_Quandl_uploads_' + str(datetime.date.today())
  completeName = os.path.join(save_path, file_name + ".txt")
  f = open(completeName, "w")

  for s in failed_data_symbols:
    print("Failed symbol: " + str(s))
    f.write("Failed: " + s + "\n")

  f.close()

"""
Utility: Some symbols from datbase need refactored
         to work for Quandl API.
"""
def format_ticker(ticker):
    if '-' in ticker:
        symbol = ticker.replace("-","_")
    else:
        symbol = ticker
    return symbol


"""
For each company, pull the pricing data from
Quandls API and save it to the database
"""
if __name__ == "__main__":
    tickers = retrieve_db_tickers(con)

    """Parameters to use to gather price data over a period of time """
    start = '2016-08-09'
    end = '2016-08-09'

    """Parameters to use to gather the most recent days price data """
    #start = datetime.date.today().strftime("%Y-%m-%d")
    #end = datetime.date.today().strftime("%Y-%m-%d")

    for t in tickers:
        print "Collecting data for: " + str(t[1])
        quandl_data = get_Quandl_daily_data(t[1], start, end)

        # The data retrieval failed for this specific ticker
        if quandl_data == -1:
            continue

        # The data retrieval was a success
        elif quandl_data:
            insert_data_into_db('2', t[0], quandl_data)

        # No data implies non-buisness day
        else:
            print "No data, so it must be a holiday or weekend. No updates for today."
            break

    #Save failed symbols off into a file for manual inspection
    if failed_data_symbols:
        generate_failure_file()



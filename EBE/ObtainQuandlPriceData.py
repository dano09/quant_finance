#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 8/10/2016

This script collects price data (Open, High, Low, Close, Adjusted Close, and Volume) henceforth referred to as
OHLCAV data, from QUANDL using their API, and saves it to the database. It does this for each company in the S&P500.
"""
import math
import os.path
import time

import quandl

from EBE.ebe_dao import *

quandl.ApiConfig.api_key = 'zmdzi5zBSfY6PsjDvvtV'
failed_data_symbols = []
con = get_db_connection()


def get_Quandl_daily_data(ticker, start, end):
    """
    Obtains price data from Quandl's API for the specificed company.
    This function is currently set to get the most recent date, but is
    capable of collecting all data within the specified start_date and
    end_date parameters. The dates are in (YYYY, M, D) format
    :param ticker: Ticker symbol that represents a company
    :param start:
    :param end:
    :return: OHLCAV data for the company
    """
    prices = []
    symbol = format_ticker(ticker)
    valid_data_flag = True

    # Attempt to connect to Quandl API and retrieve price data
    try:
        data = quandl.get("WIKI/" + symbol, start_date=start, end_date=end)
    except Exception, e:
        print "Could not download QUANDL data: %s" % e
        valid_data_flag = False
        prices = -1
        failed_data_symbols.append(ticker)

    if valid_data_flag and not data.empty:
        # Map the dataframe into a list of tuples for easy
        # database insertion
        rows_of_data = [list(x) for x in data.to_records(index=True)]

        for row in rows_of_data:
            # Format data and set precision. The tuple entries include Date, Open, High, Low,
            # Close, Adjusted Close, and Volume
            one_day_of_prices = ["%.4f" % row[1], "%.4f" % row[2],
            "%.4f" % row[3], "%.4f" % row[4], "%.4f" % row[11], row[5]]

            # Remove any nan values and include the date
            one_day_of_prices = remove_nan_values(one_day_of_prices)
            one_day_of_prices.insert(0, row[0].date())
            prices.append(one_day_of_prices)

    else:
        prices = -1
        failed_data_symbols.append(ticker)

    return prices


def remove_nan_values(daily_prices):
    """
    Utility method to replace Nan values with zeros, since they cannot be inserted into the database
    :param daily_prices: List of price data
    :return: price_data with no zeros
    """
    for index, price in enumerate(daily_prices):
        if math.isnan(float(price)):
            daily_prices[index] = 0

    return daily_prices


def generate_failure_file():
    """
    Utility: Creates file for failed tickers
    """
    save_path = '/home/justin/Desktop/Quant/error_logs'
    file_name = 'Failed_Quandl_uploads_' + str(datetime.date.today())
    complete_name = os.path.join(save_path, file_name + ".txt")
    f = open(complete_name, "w")

    for s in failed_data_symbols:
        print("Failed symbol: " + str(s))
        f.write("Failed: " + s + "\n")

    f.close()


def format_ticker(ticker):
    """
    Utility: Some symbols from database need refactored
    to work for Quandl API.
    :param ticker: A ticker symbol
    :return: The new ticker name
    """
    if '-' in ticker:
        symbol = ticker.replace("-","_")
    elif '.' in ticker:
        symbol = ticker.replace(".","_")
    else:
        symbol = ticker
    return symbol


if __name__ == "__main__":
    start_time = time.time()
    tickers = retrieve_db_tickers(con)

    """Parameters to use to gather price data over a period of time """
    # Format: 'YYYY-MM-DD'
    start = '1998-01-01'
    end = '2016-10-14'

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
            insert_data_into_db(con, '2', t[0], quandl_data)

        # No data implies non-business day
        else:
            print "No data, so it must be a holiday or weekend. No updates for today."
            break

    # Save failed symbols off into a file for manual inspection
    if failed_data_symbols:
        generate_failure_file()

    print("--- %s seconds ---" % (time.time() - start_time))

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 8/6/2016

This script makes a call to Yahoo Finance to collect price data (Open, High, Low, Close, Adjusted Close, Volume)
henceforth referred to as OHLCAV data, for every company in the S&P500 and saves it to the database.
The script was inspired by Michael Halls-Moore articles on Quantstart.com
"""

import urllib2
import httplib
import os.path
import time
from SharedFunctionsLib import *

# Using http 1.0 instead the default http/1.1 since http 1.1
# can handle the chunks, but web-servers cannot when scraping
# yahoo data.
httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
failed_data_symbols = []
con = get_db_connection()


def get_yahoos_daily_data(ticker, start_date, end_date, cron_flag):
    """
    Obtains price data from Yahoo Finance for the specified company.
    This function is currently set to get the most recent date, but is
    capable of collecting all data within the specified start_date and
    end_date parameters. The dates are in (YYYY, M, D) format
    :param ticker: Ticker symbol that represents a company
    :param start_date: Collect pricing data starting at this date
    :param end_date: Collection of pricing data ends at this date
    :param cron_flag: Boolean - True if getting data for one day, false otherwise
    :return: OHLCAV data for the company
    """
    prices = []
    # Create Yahoo URL to retrieve the CSV data for the given ticker. The month column starts at index 0 while the day
    # column starts at index 1
    yahoo_url = "http://ichart.finance.yahoo.com/table.csv?s=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s" % \
                (ticker, start_date[1] - 1, start_date[2], start_date[0], end_date[1] - 1, end_date[2], end_date[0])

    # Try connecting to Yahoo Finance and obtaining the data. Record any failed tickers for manual review and print
    # out the error message
    try:
        # We ignore the header with the [1:]
        yahoo_data = urllib2.urlopen(yahoo_url).readlines()[1:]

        # First day is the either the start of the dataset, or the day of the IPO if the company had not gone
        # public yet
        if not cron_flag:
            first_day = yahoo_data[-1].strip().split(',')
            assign_starting_date(con, ticker, first_day[0])

        for line in yahoo_data:
            p = line.strip().split(',')
            prices.append((datetime.datetime.strptime(p[0], '%Y-%m-%d'),
                           p[1], p[2], p[3], p[4], p[5], p[6]))

    except Exception, e:
        print "Could not download Yahoo data: %s" % e
        prices = -1
        failed_data_symbols.append(ticker)

    return prices


def generate_failure_file():
    """
    Utility method to create a file detailing the failed tickers
    """
    save_path = '/home/justin/Desktop/Quant/error_logs'
    file_name = 'Failed_uploads_' + str(datetime.date.today())
    complete_name = os.path.join(save_path, file_name + ".txt")
    f = open(complete_name, "w")

    for s in failed_data_symbols:
        print("Failed symbol: " + str(s))
        f.write("Failed: " + s + "\n")

    f.close()


def check_one_day(start, end):
    """
    Utility method to check if we are using this as a daily script, or over historical data. If we use
    it as a daily script, its a datetime object, otherwise we have a tuple
    """
    return start == end


if __name__ == "__main__":
    start_time = time.time()
    tickers = retrieve_db_tickers(con)

    """Parameters used to gather price data over a period of time """
    # Format: (YYYY, M, D)
    start_date = (1998, 1, 1)
    end_date = (2016, 10, 14)

    """Parameters to use to gather the most recent days price data """
    #start_date = datetime.date.today().timetuple()[0:3]
    #end_date = datetime.date.today().timetuple()[0:3]

    # Used to determine if we need to assign starting date for tickers
    history_flag = check_one_day(start_date, end_date)

    for t in tickers:
        print "Adding data for %s" % t[1]
        yahoo_data = get_yahoos_daily_data(t[1], start_date, end_date, history_flag)

        # The data retrieval failed for this specific ticker
        if yahoo_data == -1:
            continue

        # The connection was a success, insert data into the database
        elif yahoo_data:
            insert_data_into_db(con, '1', t[0], yahoo_data)
            # Sleep to prevent over-flooding of the Yahoo Servers
            time.sleep(.6)

        # No data implies non-business day
        else:
            print "No data, so it must be a holiday or weekend. No updates for today."
            break

    # Save failed symbols off into a file for manual inspection
    if failed_data_symbols:
        generate_failure_file()

    print("--- %s seconds ---" % (time.time() - start_time))


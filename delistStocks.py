#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 10/1/2016

Checks and makes sure each ticker is still used via public exchanges. Tickers can be delisted for several types of
corporate actions, such as bankruptcy, acquisitions, or mergers to name a few. If the ticker apepars to not be live
any more we update the tickers status in the database.

Both vendors behave differently when handling delisted companies. Yahoo will continue to provide price data
for future dates, but just fill with data with the last day it was traded, with no volume.
Quandls API on the other hand will not return any data once a ticker is delisted. Our cleanPricingData script will
notice this discrepancy, and stop saving data in the cleaned_price table once it notices Quandl does not return any.
Our way of verifying that a ticker is no longer listed is to check its last price data from the clean_prices table,
and if it does not match the day this script is ran, we know it has been delisted. We also give a 4 day margin in
case this script happens to run on a 3 day weekend.
"""

import datetime
from SharedFunctionsLib import *

timestamp = datetime.datetime.utcnow()


def get_month_of_data(stock):
    """
    Gets the past month of price data. We use the past month to gauge the activity of a company
    :param stock: String - ticker for a company
    :return: Dataframe - past month of OHLCAV data for a company
    """
    today = datetime.date.today()
    last_month_date = today - datetime.timedelta(days=30)
    data = retrieve_clean_data(con, stock, last_month_date, today)
    return data


def check_for_delisted_stocks(data):
    """
    Compares the last price date with todays date, which will verify if the ticker is still live or not.
    :param data: Dataframe - most recent month of OHLCAV data for a company
    :return: Either a Date object, which indicates the last day a company was live,
    or None if the company is still live
    """
    today = datetime.date.today()
    last_date = data.loc[len(data)-1][2]

    # We use margin to handle the case that the script runs on a weekend. Exchanges can only be closed for a maximum
    # of three days.
    margin = datetime.timedelta(days=4)

    live_flag = today - margin <= last_date

    if not live_flag:
        return last_date
    else:
        return None


if __name__ == "__main__":
    con = get_db_connection()
    tickers = retrieve_db_tickers(con)

    for ticker in tickers:
        month_of_data = get_month_of_data(ticker[1])
        delisted_day = check_for_delisted_stocks(month_of_data)
        if delisted_day:
            print "Ticker: " + str(ticker[1]) + "'s last day is : " + str(delisted_day)
            update_symbols(con, ticker[1], delisted_day)




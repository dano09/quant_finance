#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# Author: Justin Dano 8/6/2016

Interpolate any zero or nan values that were created from inconsistent pricing data from our
two vendors Yahoo Finance and Quandl. Can be used on historical data, or setup to be ran everyday.
If ran everyday, it interpolates the value four days prior to today's date.
"""
import math
import time

import holidays
import numpy as np
from bdateutil import isbday

from EBE.ebe_dao import *

timestamp = datetime.datetime.utcnow()
con = get_db_connection()


def one_day(start_day):
    """
    Utility method to check if we are using this as a daily script, or over historical data. If we use
    it as a daily script, its a datetime object, otherwise we have a string
    :param start_day:
    :return: A Boolean indicating what kind of interpolating we are doing
    """
    if isinstance(start_day, datetime.datetime):
        return True
    else:
        return False


def get_elapsed_time_window(target_date):
    """
    We interpolate with a trailing window of 4 days to account for 3 day weekends
    :param target_date: Date - Target date for processing
    :return: Date - Elapsed start date
    """
    elapsed_start = (target_date - datetime.timedelta(days=4)).strftime("%Y-%m-%d")

    return elapsed_start


def process_data(stock_tickers, start_time, end_time, history_flag):
    """
    For each ticker, gets data from the database and converts zeros to Nans for interpolation. It then
    adds the cleaned data to a new database table cleaned_prices
    :param stock_tickers: A List of tickers from the S&P 500
    :param start_time: Date we use to start the processing
    :param end_time: Date we use to end processing
    :param history_flag: Used to know what day to insert the data into the database
    :return:
    """
    for t in stock_tickers:
        print "Interpolating price data for ticker: " + t[1]
        stock_data = retrieve_data_with_zeros(con, t[1], start_time, end_time)
        if isinstance(stock_data, pd.DataFrame):
            price_data = stock_data[
                ['open_price', 'high_price', 'low_price', 'close_price', 'adj_close_price', 'volume']]

            # Replace zeros with Nan
            price_data = price_data.where(price_data != 0, np.nan)

            # Interpolation is done column at a time (e.g. Opens, then Highs, then Lows...etc.)
            for feature in price_data:
                stock_data[feature] = interpolate_data(feature, price_data)

            stock_data['last_updated_date'] = timestamp

            # If over historical data, no additional work is needed -- just add to database
            if history_flag:
                insert_clean_and_interpolated_data_into_db(con, stock_data)

            # If done via a cron job, need to update the target_date, then add to database
            else:
                target_day = get_elapsed_time_window(datetime.datetime.now())
                stock_data = stock_data.loc[stock_data['price_date'] == target_day]
                insert_clean_and_interpolated_data_into_db(con, stock_data)


def interpolate_data(column, data_with_zeros):
    """
    Takes all zeros from a given feature (Open, High, Low, Close, Adjusted_Close, and interpolates them.
    If the first value is zero, fill it with the next non-zero value.
    :param column: A Series object that contains time-series data for a given feature.
    :param data_with_zeros: A Dataframe object holding the data for each column/feature we want to interpolate.
    :return: A new Series object that has been processed.
    """
    new_series = data_with_zeros[column].astype(float).interpolate()

    # If the first value is NAN, we find the next day (closest in time) that is non-NAN and fill it with that value
    if math.isnan(new_series[0]):
        for row in new_series.iteritems():
            if not math.isnan(row[1]):
                new_series[0] = row[1]
                break

    return new_series


if __name__ == "__main__":
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    start_time = time.time()
    history_flag = False
    tickers = retrieve_db_tickers(con)

    """Parameters used to gather price data over a period of time """
    # Format: 'YYYY-MM-DD'
    #start = '1998-01-01'
    #end = '2016-10-14'

    """Parameters to use to gather the most recent days price data """
    start = (datetime.datetime.now() - datetime.timedelta(days=4))
    end = (datetime.datetime.now() - datetime.timedelta(days=4))

    # Used as Cron script
    if one_day(start):
        if isbday(start, holidays=holidays.US()):
            elapsed_start = get_elapsed_time_window(start)
            process_data(tickers, elapsed_start, today, history_flag)

    # Used over history
    else:
        history_flag = True
        process_data(tickers, start, end, history_flag)

    print("--- %s seconds ---" % (time.time() - start_time))

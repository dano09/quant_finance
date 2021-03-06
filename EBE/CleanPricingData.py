#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 8/21/2016

This script cleans the price data by cross referencing OHLCAV data from vendors Yahoo Finance and Quandl. This
script is designed to be ran everyday, but has the ability to clean data over a range of dates by adjusting the
@{start} and @{end} parameters in the main method.
"""
import sys
import time
from decimal import Decimal

import holidays
from bdateutil import isbday

from EBE.ebe_dao import *

con = get_db_connection()
timestamp = datetime.date.today()


def verify_price(symbol_id, y_data, q_data):
    """
    Verifies the OHLCAV data from Quandl and Yahoo for a given company, accounting
    for missing dates of data, missing entries of data (e.g. No closing price), and differences in
    precision. If one of the vendors is missing a date, we use the other vendors
    data. If both both vendors have different values for the same data point, we
    assign it zero. All zero entries will be reevaluated in the spike script.
    :param symbol_id: Used to identify the company
    :param y_data: OHLCAV Dataframe from Yahoo Finance
    :param q_data: OHLCAV Dataframe from Quandl
    :return: Dataframe of the cross referenced prices from Yahoo and Quandl
    """
    number_of_data_points = 0
    number_of_days = 0
    invalid_data_points = 0
    verified_prices = pd.DataFrame(columns=['price_date',
                                            'created_date', 'last_updated_date', 'open_price', 'high_price',
                                            'low_price', 'close_price', 'adj_close_price', 'volume'])

    # Gets the earliest and latest date. Used to handle the edge case
    # where we might have one vendors range of data differ from the others
    start_date, last_date = get_date_ranges(y_data, q_data)

    # Iterate through the dates, ignoring non-business days
    for date in pd.bdate_range(start_date, last_date):
        # Make sure to exclude American holidays
        if isbday(date, holidays=holidays.US()):
            zero_counter = 0
            number_of_data_points += 4
            number_of_days += 1
            print "Processing prices for: " + date.strftime("%Y-%m-%d")
            new_data_row = [symbol_id, date, timestamp, timestamp]
            y_daily_price = None
            q_daily_price = None
            # Convert Pandas Timestamp to a Date (YYYY-mm-DD)
            date = date.to_datetime().date()

            # Only pull the OHLCAV data if it is exists in the Dataframe
            if isinstance(y_data, pd.DataFrame):
                if not (y_data.loc[y_data['price_date'] == date]).empty:
                    y_daily_price = y_data.loc[y_data['price_date'] == date]

            if isinstance(q_data, pd.DataFrame):
                if not (q_data.loc[q_data['price_date'] == date]).empty:
                    q_daily_price = q_data.loc[q_data['price_date'] == date]

            # Determine if either vendor is missing data
            temp_prices = check_date(date, y_daily_price, q_daily_price)

            # Case 1: Only one vendor had data for the specific date, so we will use that vendors data
            if isinstance(temp_prices, pd.DataFrame):
                ohlcav_data_row = format_data(temp_prices)
                new_data_row.extend(ohlcav_data_row)
                zero_counter = 4

            # Case 2: Neither vendor had data, so we assign zeros to all values for this date
            elif not temp_prices:
                print "Neither Vendor had data for " + date.strftime(
                    "%Y-%m-%d") + " so we will fill the days price data with zeros"
                new_data_row.extend([0, 0, 0, 0, 0, 0])
                # Excluding Volume and Adjusted Close
                zero_counter = 4

            # Case 3: Compare the OHLCAV data
            else:
                yOHLCAV = format_data(y_daily_price)
                qOHLCAV = format_data(q_daily_price)

                data_row, zero_counter = compare_price_data(yOHLCAV, qOHLCAV)
                new_data_row.extend(data_row)

            # Create dataframe row from list of values
            price_df = pd.DataFrame(data=[new_data_row], columns=['symbol_id', 'price_date',
                                                                  'created_date', 'last_updated_date', 'open_price',
                                                                  'high_price', 'low_price',
                                                                  'close_price', 'adj_close_price', 'volume'])

            # Add the new price data for the specific date to our dataframe
            verified_prices = verified_prices.append(price_df, ignore_index=True)

            invalid_data_points += zero_counter
        else:
            print str(date.strftime("%Y-%m-%d")) + " is a US holiday!"

    stats_and_data = [verified_prices, number_of_data_points, invalid_data_points, number_of_days]
    return stats_and_data


def compare_price_data(yOHLCAV, qOHLCAV):
    """
    This method does the actual comparison of OHLCAV data for both vendors
    :param yOHLCAV: Dataframe - Yahoo price data
    :param qOHLCAV: Dataframe - Quandl price data
    :return: List - Price data that has been cross referenced
             Int - The number of inconsistencies
    """
    zero_counter = 0
    data_row = []
    """
    Ignoring Adjusted Price and Volume since they are almost never identical for historic data.
    We use Quandl by default. Yahoo rounds its Adjusted Price valuations, and its volume is known be incorrect
    """
    for i in range(len(yOHLCAV) - 2):
        # Easy case, the values are equivalent
        if yOHLCAV[i] == qOHLCAV[i]:
            data_row.append(yOHLCAV[i])
        else:
            precision_price = check_precision(yOHLCAV[i], qOHLCAV[i])
            # If one of the values is more precise, use that one
            if precision_price:
                data_row.append(precision_price)
            else:
                if yOHLCAV[i] == 0:
                    data_row.append(qOHLCAV[i])
                elif qOHLCAV[i] == 0:
                    data_row.append(yOHLCAV[i])
                # Cannot determine correct value, so assign
                # zero. We will use the spike filter to pad
                # the inconsistent data points
                else:
                    data_row.append(0)
                    zero_counter += 1

    # Add back quandl's adjusted close and volume
    data_row.append(qOHLCAV[-2])
    data_row.append(qOHLCAV[-1])
    return data_row, zero_counter


def get_date_ranges(y_data, q_data):
    """
    Compares the earliest and latest date from both vendors, and returns the earliest
    and latest. We make no assumption that both vendors have all the data specified
    in the main method.
    :param y_data: Yahoo Finance Data
    :param q_data: Qunadl Finance Data
    :return:

    Ex. Yahoo -  2016-01-01 : 2016-01-10
        Quandl - 2016-01-01 : 2016-01-09
        returns - 2016-01-01, 2016-01-10
    """
    if not isinstance(y_data, pd.DataFrame):
        first_date = q_data['price_date'].min()
        last_date = q_data['price_date'].max()
    elif not isinstance(q_data, pd.DataFrame):
        first_date = y_data['price_date'].min()
        last_date = y_data['price_date'].max()
    else:
        first_date = min([y_data['price_date'].min(), q_data['price_date'].min()])
        last_date = min([y_data['price_date'].max(), q_data['price_date'].max()])

    return first_date, last_date


def check_date(date, y_price, q_price):
    """
    Checks to see if the data is provided by both vendors on a specific date. If
    one of the vendors is missing data, we will use the other vendors data by default.

    TODO: All because one of the vendors is empty, does not mean the other vendor
    has accurate data. We could try to call the failed vendor again for the specific date
    before continuing cross-referencing the prices
    :param date: The day we are comparing vendor data on
    :param y_price: Yahoo OHLCAV data for @{date}
    :param q_price: Quandls OHLCAV data for @{date}
    :return: Dataframe of data (if the other vendor is missing data)
             True if both have data
             None if neither have data
    """
    if not isinstance(y_price, pd.DataFrame) and isinstance(q_price, pd.DataFrame):
        print "Yahoo did not have data, so we will use Quandl's price data for " + date.strftime("%Y-%m-%d")
        return q_price
    elif not isinstance(q_price, pd.DataFrame) and isinstance(y_price, pd.DataFrame):
        print "Quandl did not have data, so we will use Yahoo's price data for " + date.strftime("%Y-%m-%d")
        return y_price
    elif not isinstance(y_price, pd.DataFrame) and not isinstance(q_price, pd.DataFrame):
        return None
    else:
        return True


def check_precision(y_price, q_price):
    """
    If the prices are the same, except one vendor
    used more precision, use the more precise value.
    Otherwise, return false.
    :param y_price: Yahoo Finance Price Data
    :param q_price: Quandl Price Data
    :return: The more precise value

    Ex: yPrice = 15.501
        qPrice = 15.50
        return 15.501
    """
    y_dec = str(Decimal(y_price).normalize())
    q_dec = str(Decimal(q_price).normalize())

    precision_price = False
    if len(y_dec) > len(q_dec):
        if q_dec in y_dec:
            precision_price = y_price
    elif len(y_dec) < len(q_dec):
        if y_dec in q_dec:
            precision_price = q_price

    return precision_price


def format_data(daily_price_data):
    """
    Format data to fit the data types we use in the database.
    """
    return ["%.4f" % daily_price_data['open_price'], "%.4f" % daily_price_data['high_price'],
            "%.4f" % daily_price_data['low_price'], "%.4f" % daily_price_data['close_price'],
            "%.4f" % daily_price_data['adj_close_price'], long(daily_price_data['volume'])]


def print_stats(total_points, invalid_points, tickers, days, first_day, last_day):
    """
    Print out stats of script parameters
    """
    print "\nStarting date:            " + str(first_day)
    print "Ending date:              " + str(last_day)
    print "Total Business days:      " + str(days)
    print "Total Companies analyzed: " + str(tickers)
    print "Total OHLC data points:   " + str(total_points)
    print "Inconsistent data points: " + str(invalid_points)
    print "Discrepancy percentage:   " + str("%.2f" % ((float(invalid_points) / float(total_points)) * 100)) + "%"


if __name__ == "__main__":
    start_time = time.time()
    total_data_points = 0
    invalid_data_points = 0
    total_tickers = 0
    total_days = 0

    """Parameters to use to gather price data over a period of time """
    # Format: 'YYYY-MM-DD'
    start = '1998-01-01'
    end = '2016-10-13'


    """Parameters to use to gather the most recent days price data """
    #start = datetime.date.today().strftime("%Y-%m-%d")
    #end = datetime.date.today().strftime("%Y-%m-%d")

    # When just updating the most recent day, end the script if it is not a business day
    if start == end:
        if not isbday(start, holidays=holidays.US()):
            print "Not a business day, ending program."
            sys.exit()

    tickers = retrieve_db_tickers(con)
    # Collect data for each company
    for t in tickers:
        total_tickers += 1
        print "Cleaning price data for ticker: " + t[1]

        # Gather initial datasets from both vendors
        yahoo_data = retrieve_price_data(con, t[1], 1, start, end)
        quandl_data = retrieve_price_data(con, t[1], 2, start, end)

        if isinstance(yahoo_data, pd.DataFrame) or isinstance(quandl_data, pd.DataFrame):
            # Clean data and add to the database
            stats_and_data = verify_price(t[0], yahoo_data, quandl_data)
            total_data_points += stats_and_data[1]
            invalid_data_points += stats_and_data[2]

            if stats_and_data[3] > total_days:
                total_days = stats_and_data[3]

            insert_clean_data_into_db(con, stats_and_data[0])
        else:
            print "Ticker data could not be found, skipping ticker"

    print_stats(total_data_points, invalid_data_points, total_tickers, total_days, start, end)
    print("Time to complete:         %s seconds" % round((time.time() - start_time), 4))

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Justin Dano 8/6/2016
#

import datetime
import MySQLdb as mdb
import sys
import pandas as pd
import numpy as np
import math
from SharedFunctionsLib import *
import holidays
from bdateutil import isbday

timestamp = datetime.datetime.utcnow()

def one_day(start_day):
	"""

	:param start_day:
	:return:
	"""
	if isinstance(start_day, datetime.datetime):
		return True
	else:
		return False

def get_elapsed_time_window(start):
	"""

	:param start:
	:return:
	"""
	start_date = (start - datetime.timedelta(days=4)).strftime("%Y-%m-%d")
	end_date = datetime.datetime.now().strftime("%Y-%m-%d")

	return start_date, end_date


def process_data(stock_tickers, start_time, end_time, history_flag):
	"""

	:param stock_tickers:
	:param start_time:
	:param end_time:
	:param history_flag:
	:return:
	"""
	for t in stock_tickers:
		print "Interpolating price data for ticker: " + t[1]
		stock_data = retrieve_data_with_zeros(con, t[1], start_time, end_time)
		if isinstance(stock_data, pd.DataFrame):
			price_data = stock_data[['open_price', 'high_price', 'low_price', 'close_price', 'adj_close_price', 'volume']]
			price_data = price_data.where(price_data != 0, np.nan)

			for feature in price_data:
				stock_data[feature] = interpolate_data(feature, price_data)

			stock_data['last_updated_date'] = timestamp
			if history_flag:
				insert_data_into_db(con, stock_data)
			else:
				#print "STOCK DATA IS:"
				#print stock_data
				target_day = (datetime.datetime.now() - datetime.timedelta(days=4)).strftime("%Y-%m-%d")
				stock_data = stock_data.loc[stock_data['price_date'] == target_day]
				#print "STOCK_DATA IS: "
				#print stock_data
				#sys.exit()
				insert_data_into_db(con, stock_data)

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
	"""
	Interpolate any zero or nan values that were created from inconsistent pricing data from our
	two vendors Yahoo Finance and Quandl. Can be used on historical data, or setup to be ran everyday.
	If ran everyday, it interpolates the value four days prior to todays date.
	"""
	# Loop over the tickers and insert the daily historical
	# data into the database
	history_flag = False
	con = get_db_connection()
	tickers = retrieve_db_tickers(con)

	"""Parameters used to gather price data over a period of time """
	# Format: 'YYYY-MM-DD'
	start = '2016-08-01'
	end = '2016-09-16'

	"""Parameters to use to gather the most recent days price data """
	#start = (datetime.datetime.now() - datetime.timedelta(days=4))
	#end = (datetime.datetime.now() - datetime.timedelta(days=4))

	# Used as Cron script
	if one_day(start):
		if isbday(start, holidays=holidays.US()):
			elapsed_start, today = get_elapsed_time_window(start)
			process_data(tickers, elapsed_start, today, history_flag)

	# Used over history
	else:
		history_flag = True
		process_data(tickers, start, end, history_flag)



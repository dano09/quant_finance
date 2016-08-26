#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 8/21/2016

This script cleans the price data by cross referencing 
OHLCAV data from vendors Yahoo Finance and Quandl. This
script is designed to be ran everyday, but has the ability
to clean data over a range of dates by adjusting the 
@{start} and @{end} parameters in the main method.
"""
import datetime
import MySQLdb as mdb
import sys
import pandas as pd
import numpy as np
from decimal import Decimal
from pandas.tseries.offsets import *
from bdateutil import isbday
import holidays
from SharedFunctionsLib import *

# Obtain a database connection to the MySQL instance
db_host = 'localhost'
db_user = '****'
db_pass = '****'
db_name = '****'
con = mdb.connect(db_host, db_user, db_pass, db_name)
timestamp = datetime.date.today()


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
Retrive price data from the database for the specific
ticker over the specified range.

    ticker - The company's ticker symbol
    vendor_id - The vendor we grab the price data from
    start - We grab data starting at this date
    end - The data ends at this date 
    returns - Dataframe of all the price data
"""        
def retrieve_price_data(ticker, vendor_id, start, end):
    with con: 
        cur = con.cursor()
        # First query is to retrieve the id for the given symbol
        cur.execute("SELECT id FROM symbol WHERE ticker = %s", [ticker])
        ticker_id = cur.fetchall()
        ticker_id = ticker_id[0][0]
        # Second query gathers OHLCAV data  
        cur.execute("SELECT * FROM daily_price WHERE \
        symbol_id = %s AND data_vendor_id = %s \
        AND price_date BETWEEN %s AND %s", (ticker_id, vendor_id, start, end))
        
        # Return none if no data exists for the ticker within the specified 
        # time frame, otherwise return a dataframe with the OHLCAV data
        if not cur.rowcount:
            if vendor_id == 1:
                print "Yahoo had no price data available for " + str(start)
            else:
                print "Quandl had no price data available for " + str(start)
            priceData = None
        else:
            priceData = pd.DataFrame(list(cur.fetchall()))
            priceData.columns = ['id','symbol_id','vendor_id','price_date','created_date',
            'last_updated_date','open_price','high_price','low_price','close_price',
            'adj_close_price','volume']

        return priceData

"""
Verifies the OHLCAV data from Quandl and Yahoo for a given company, accounting 
for missing dates of data, missing entries of data, and differences in
precision. If one of the vendors is missing a date, we use the other vendors 
data. If both both vendors have different values for the same data point, we
assign it zero. All zero entries will be reevaluated in the spike script.

    symbolId - Used to identify the company
    yData - OHLCAV Dataframe from Yahoo Finance
    qData - OHLCAV Dataframe from Quandl
    returns - Dataframe of the cross referenced prices from Yahoo and Quandl
"""    
def verify_price(symbolId, yData, qData):

    verifiedPrices  = pd.DataFrame(columns=['price_date',
    'created_date','last_updated_date','open_price','high_price',
    'low_price','close_price','adj_close_price','volume'])
    
    # Gets the earliest and latest date. Used to remediate the edge case
    # where we might have one vendors range of data differ from the others
    start_date, last_date = get_date_ranges(yData,qData)

    # Iterate through the dates, ignoring non-business days
    for date in pd.bdate_range(start_date, last_date):
        # Make sure to excluse American holidays
        if isbday(date, holidays=holidays.US()):
            print "Processing prices for: " + date.strftime("%Y-%m-%d")
            newDataRow = [symbolId, date, timestamp, timestamp]
            yDailyPrice = None
            qDailyPrice = None

            # Only pull the OHLCAV data if it is exists in the Dataframe
            if isinstance(yData, pd.DataFrame):
                if not (yData.loc[yData['price_date'] == date]).empty:
                    yDailyPrice = yData.loc[yData['price_date'] == date]

            if isinstance(qData, pd.DataFrame):
                if not (qData.loc[qData['price_date'] == date]).empty:
                    qDailyPrice = qData.loc[qData['price_date'] == date]
                
            # Determine if either vendor is missing data
            tempPrices = checkDate(date, yDailyPrice, qDailyPrice)

            # Case 1: Only one vendor had data for the specific date,
            # so we will use that vendors data
            if isinstance(tempPrices, pd.DataFrame):
                ohlcavDataRow = format_data(tempPrices)
                newDataRow.extend(ohlcavDataRow)
        
            # Case 2: Neither vendor had data, so we assign zeros
            # to all values for this date
            elif not tempPrices:
                print "Neither Vendor had data for " + date.strftime("%Y-%m-%d") + " so we will fill the days price data with zeros"
                newDataRow.extend([0,0,0,0,0,0])
            
            # Case 3: Compare the OHLCAV data
            else:
                yOHLCAV = format_data(yDailyPrice)
                qOHLCAV = format_data(qDailyPrice)
                
                dataRow = compare_price_data(yOHLCAV, qOHLCAV)
                newDataRow.extend(dataRow)

            # Create dataframe row from list of values
            priceDF = pd.DataFrame(data=[newDataRow], columns=['symbol_id','price_date',
            'created_date','last_updated_date','open_price','high_price','low_price',
            'close_price','adj_close_price','volume'])
        
            # Add the new price data for the specific date to our dataframe
            verifiedPrices = verifiedPrices.append(priceDF, ignore_index=True)
            
        else:
            print str(date.strftime("%Y-%m-%d")) + " is a US holiday!"
            
    return verifiedPrices
    
"""
This method does the actual comparison of OHLCAV data for both vendors

    yOHLCAV - Yahoo price data
    qOHLCAV - Quandl price data
    
    returns - list of price data that has been cross referenced 
"""
def compare_price_data(yOHLCAV, qOHLCAV):    
    # Compare values for Open, High, Low, Close
    # Adj Close, and Volume 
    volumeData = 0
    dataRow = []
    for i in range(len(yOHLCAV)):
        '''
        For volume, Quandl is used by default. Its an aggregate for 
        all US volume over all exchanges. Yahoo does not provide 
        information on how it derives its volume, so we stick with Quandl.
        '''
        if isinstance(yOHLCAV[i], long):
            volumeData = qOHLCAV[i]
        # All other values
        else:
                
            # Easy case, the values are equivalent
            if yOHLCAV[i] == qOHLCAV[i]:
                dataRow.append(yOHLCAV[i])
            else:
                precisionPrice = checkPrecision(yOHLCAV[i],qOHLCAV[i])
                # If one of the values is more precise, use that one
                if precisionPrice:
                    dataRow.append(precisionPrice)
                else:
                    if yOHLCAV[i] == 0:
                        dataRow.append(qOHLCAV[i])
                    elif qOHLCAV[i] == 0:
                        dataRow.append(yOHLCAV[i])
                    # Cannot determine correct value, so assign
                    # zero. We will use the spike filter to pad 
                    # the inconsistent data points
                    else:
                        dataRow.append(0)
                    
    dataRow.append(volumeData)
    return dataRow
    
    
"""
Compares the earliest and latest date from both vendors, and returns the earliest
and latest. We make no assumption that both vendors have all the data specified
in the main method.

    Ex. Yahoo -  2016-01-01 : 2016-01-10
        Quandl - 2016-01-01 : 2016-01-09
        
        returns - 2016-01-01, 2016-01-10    
"""
def get_date_ranges(yData,qData):

    if not isinstance(yData, pd.DataFrame):
        first_date = qData['price_date'].min()
        last_date = qData['price_date'].max()
    elif not isinstance(qData, pd.DataFrame):
        first_date = yData['price_date'].min()
        last_date = yData['price_date'].max()
    else:
        first_date = min([yData['price_date'].min(), qData['price_date'].min()])
        last_date = min([yData['price_date'].max(), qData['price_date'].max()])
        
    return first_date, last_date    

"""
Checks to see if the data is provided by both vendors on a specific date. If
one of the vendors is missing data, we will use the other vendors data by default.

    date - Used to log which vendor is missing data
    yPrice - Yahoo OHLCAV data for @{date}
    qPrice - Quandls OHLCAV data for @{date}
    
    returns - Dataframe of data (if the other vendor is missing data)
              True if both have data
              None if neither have data
"""
def checkDate(date, yPrice, qPrice):
    '''TODO: All because one of the vendors is empty, does not mean the other vendor
        has accurate data. We could try to call the failed vendor again for the specific date
        before continuing cross-referencing the prices
    '''
    if not isinstance(yPrice, pd.DataFrame) and isinstance(qPrice, pd.DataFrame):
        print "Yahoo did not have data, so we will use Quandl's price data for " + date.strftime("%Y-%m-%d")
        return qPrice
    elif not isinstance(qPrice, pd.DataFrame) and isinstance(yPrice, pd.DataFrame):
        print "Quandl did not have data, so we will use Yahoo's price data for " + date.strftime("%Y-%m-%d")
        return yPrice
    elif not isinstance(yPrice, pd.DataFrame) and not isinstance(qPrice, pd.DataFrame):
        return None
    else:
        return True
        
"""
Utility: If the prices are the same, except one vendor
         used more precision, use the more precise value.
         Otherwise, return false.
         
         Ex. yPrice = 15.501
             qPrice = 15.50
             return yPrice
"""  
def checkPrecision(yPrice, qPrice):
    yDec = str(Decimal(yPrice).normalize())
    qDec = str(Decimal(qPrice).normalize())

    precisionPrice = False
    if len(yDec) > len(qDec):
        if qDec in yDec:
            precisionPrice = yPrice
    elif len(yDec) < len(qDec):
        if yDec in qDec:
            precisionPrice = qPrice

    return precisionPrice
            
"""
Utility: Format data to fit the data types we use in the database.
"""    
def format_data(dailyPriceData):
    return ["%.4f" % dailyPriceData['open_price'], "%.4f" % dailyPriceData['high_price'], 
    "%.4f" % dailyPriceData['low_price'], "%.4f" % dailyPriceData['close_price'], 
    "%.4f" % dailyPriceData['adj_close_price'], long(dailyPriceData['volume'])]
    
"""
Takes the OHLCAV data for a specific company, over a pre-defined
time range and adds it to the Database.

  data_vendor_id - Identification for Quandl
  symbol_id - What we use to relate the ticker and price data 
  daily_data - List of tuples of the OHLCAV data 
"""
def insert_data_into_db(price_data): 
    #Add Dataframe to the SQL Database table clean_prices
    with con: 
        price_data.to_sql(con=con, name='clean_prices', if_exists='append', index= False, flavor='mysql')

    
if __name__ == "__main__":
    
    """Parameters to use to gather price data over a period of time """
    start = '2016-08-01'
    end = '2016-08-19'
    
      """Parameters to use to gather the most recent days price data """
    #start = datetime.date.today().strftime("%Y-%m-%d")
    #end = datetime.date.today().strftime("%Y-%m-%d")
    
    # When just updating the most recent day, end the script
    # if it is not a business day
    if start == end:    
        if not isbday(start, holidays=holidays.US()):
            print "Not a business day, ending program."
            sys.exit()
            
    tickers = retrieve_db_tickers()
    # Collect data for each company
    for t in tickers:
        print "Cleaning price data for ticker: " + t[1] 
        
        # Gather initial datasets from both vendors
        yahooData = retrieve_price_data(t[1], 1, start, end)
        quandlData = retrieve_price_data(t[1], 2, start, end)
        
        # Clean data and add to the database
        prices = verify_price(t[0], yahooData, quandlData)
        print "Inserting the following dataframe for ticker: " + t[1]
        print prices
        insert_data_into_db(prices)
        

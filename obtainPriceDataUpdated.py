#!/usr/bin/python
# -*- coding: utf-8 -*-

#Author: Justin Dano 8/6/2016
#This script was inspired by Michael Halls-Moore articles on Quantstart.com

import datetime
import MySQLdb as mdb
import urllib2
import httplib
import time
import os.path
from SharedFunctionsLib import *

# Using http 1.0 instead the default http/1.1 since http 1.1 
# can handle the chunks, but web-servers cannot when scraping
# yahoo data.
httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
timestamp = datetime.datetime.utcnow()
failed_data_symbols = []
        
# Obtain a database connection to the MySQL instance
db_host = 'localhost'
db_user = '*********'
db_pass = '*********'
db_name = 'securities_master3'
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
Obtains price data from Yahoo Finance for the specificed company.
This function is currently set to get the most recent date, but is
capable of collecting all data within the specified start_date and 
end_date parameters. The dates are in (YYYY, M, D) format

    ticker -    Ticker symbol that represents a company
    start_date - Collect pricing data starting at this date
    end_date - Collection of pricing data ends at this date
    returns - OHLCAV data for the company
"""
def get_Yahoos_daily_data(ticker, start_date, end_date):
    prices = []
    # Create Yahoo URL to retrieve the CSV data for the given ticker.
    # The month column starts at index 0 while the day column starts 
    # at index 1
    yahoo_url = "http://ichart.finance.yahoo.com/table.csv?s=%s&a=%s&b=%s&c=%s&d=%s&e=%s&f=%s" % \
        (ticker, start_date[1] - 1, start_date[2], start_date[0], 
        end_date[1] - 1, end_date[2], end_date[0])
    
    # Try connecting to Yahoo Finance and obtaining the data
    # Record any failed tickers for manual review and print 
    # out the error message
    try:
        #We ignore the header with the [1:]
        yahoo_data = urllib2.urlopen(yahoo_url).readlines()[1:]                

        for line in yahoo_data:
            p = line.strip().split(',')
            prices.append((datetime.datetime.strptime(p[0], '%Y-%m-%d'),
                p[1], p[2], p[3], p[4], p[5], p[6]))

    except Exception, e:
        print "Could not download Yahoo data: %s" % e
        prices = -1
        failed_data_symbols.append(ticker)
    
    return prices

"""
Takes the OHLCAV data for a specific company, over pre-defined
time range and adds it to the Database.

    data_vendor_id - Identification for Yahoo
    symbol_id - What we use to relate the ticker and price data 
    daily_data - List of tuples of the OHLCAV data 
"""
def insert_data_into_db(data_vendor_id, symbol_id, daily_data): 
    # Map daily price information to the columns of our database table
    daily_data = [(data_vendor_id, symbol_id, d[0], timestamp, timestamp,
        d[1], d[2], d[3], d[4], d[5], d[6]) for d in daily_data]

    # Create the insert strings
    column_str = """data_vendor_id, symbol_id, price_date, created_date, 
                    last_updated_date, open_price, high_price, low_price, 
                    close_price, volume, adj_close_price"""
    insert_str = ("%s, " * 11)[:-2]
    query_string = "INSERT INTO daily_price2 (%s) VALUES (%s)" % (column_str, insert_str)
    
    #Connect with MySQL database and perform the insert query
    with con: 
        cur = con.cursor()
        cur.executemany(query_string, daily_data)

"""
Utility method to create a file detailing the failed tickers

"""
def generate_failure_file():
    save_path = 'C:/Users/Justin/Desktop/Quant'
    file_name = 'Failed_uploads_' + str(datetime.date.today())
    completeName = os.path.join(save_path, file_name + ".txt")    
    f = open(completeName, "w")     

    for s in failed_data_symbols:
        print("Failed symbol: " + str(s))
        f.write("Failed: " + s + "\n") 
        
    f.close()


if __name__ == "__main__":
    # Loop over the tickers and insert the daily historical
    # data into the database
    tickers = retrieve_db_tickers()

    """Parameters used to gather price data over a period of time """
    start_date = (2016,8,2)
    end_date = (2016,8,6)

    """Parameters to use to gather the most recent days price data """
    #start_date = datetime.date.today().timetuple()[0:3]
    #end_date = datetime.date.today().timetuple()[0:3]

    for t in tickers:
        print "Adding data for %s" % t[1]
        yahoo_data = get_Yahoos_daily_data(t[1], start_date, end_date)
        
        # The data retrieval failed for this specific ticker
        if yahoo_data == -1:
            continue

        # The connection was a success 
        elif yahoo_data:
            insert_data_into_db('1', t[0], yahoo_data)
            #Sleep to prevent overflooding of the Yahoo Servers 
            time.sleep(.6) 

        # No data implies non-buisness day    
        else:
            print "No data, so it must be a holiday or weekend. No updates for today."
            break

    #Save failed symbols off into a file for manual inspection
    if failed_data_symbols:
        generate_failure_file()

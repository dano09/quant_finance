#!/usr/bin/python
# -*- coding: utf-8 -*-

#Author: Justin Dano 8/6/2016
#This script was inspired by Michael Halls-Moore articles on Quantstart.com

import datetime
import lxml.html
import MySQLdb as mdb
import sys
from urllib2 import urlopen
from lxml import etree
from math import ceil
from io import StringIO

#Initalize datbase connection
db_host = 'localhost'
db_user = '*********'
db_pass = '*********'
db_name = 'securities_master3'
con = mdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)

"""
Scrape S&P500 symbols from Wikipedia page 

    returns - List of current SP500 symbols
"""
def scrape_SNP500_symbols():
    #Timestamp used for created_at column in database
    timestamp = datetime.datetime.utcnow()

    # Use libxml to scrape S&P500 ticker symbols
    page = urlopen('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    page = lxml.html.parse(page)
    symbols_list = page.xpath('//table[1]/tr')[1:]

    # Obtain the ticker symbol, name, and sector information 
    # for each row in the S&P500 constituent table
    ticker_symbols = []
    for symbol in symbols_list:
        tds = symbol.getchildren()
        sd = {'ticker': tds[0].getchildren()[0].text,
                'name': tds[1].getchildren()[0].text,
                'sector': tds[3].text}

        # Map ticker information to the columns of our database table
        ticker_symbols.append((sd['ticker'], 'stock', sd['name'], 
            sd['sector'], 'USD', timestamp, timestamp))

    return ticker_symbols

"""
If we are updating our symbols table, we do not want to 
add duplicate symbols, so here we filter out companies 
that already exist in the database.

    symbols - The list of symbols scraped from Wikipedia
    returns - List of symbols not yet represented in database
"""
def filter_symbols(symbols):    
    new_symbols = [] 
    unique_symbols = set() 

    # Connect to the MySQL instance
    #con = mdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)
    with con: 
        cur = con.cursor()
        cur.execute("SELECT id, ticker FROM symbol")
        data = cur.fetchall()

        #First get all ticker symbols for the database
        for symbol in data:
            unique_symbols.add(symbol[1])
                
        # Now add any additional symbols not yet included in the
        # database from the SP500 wiki page 
        for s in symbols:
            if s[0] not in unique_symbols:
                print(str(s[0]) + " will be added to the database!")
                new_symbols.append(s)
        return new_symbols    

"""
Insert any new S&P500 symbols (that do not already belong) 
into the MySQL database.

    symbols - Ticker information on current S&P500 that 
                        does not yet exist in our database 
"""
def insert_SNP500_symbols(symbols):
    # Create the insert query
    column_fields = "ticker, instrument, name, sector, currency, created_date, last_updated_date"
    insert_fields = ("%s, " * 7)[:-2]
    query_string = "INSERT INTO symbol (%s) VALUES (%s)" % (column_fields, insert_fields)
    
    #Insert symbol data into the database for every symbol
    with con: 
        cur = con.cursor()
        # This line avoids the MySQL MAX_PACKET_SIZE
        # It chunks the inserts into sets of 100 at a time
        for i in range(0, int(ceil(len(symbols) / 100.0))):
            cur.executemany(query_string, symbols[i*100:(i+1)*100-1])


if __name__ == "__main__":

    #1. Scrape ticker data for the current companies existing
    #     in the S&P500 index from Wikipedia
    symbols = scrape_SNP500_symbols()

    #2. Filter out pre-existing data that may already belong
    #     in our database
    filtered_symbols = filter_symbols(symbols)

    #3. Insert company ticker data into our MySQL database
    insert_SNP500_symbols(filtered_symbols)

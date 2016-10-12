#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 8/6/2016

This script scrapes S&P500 tickers from wikipedia and saves it to the database. The script was inspired by
Michael Halls-Moore articles on Quantstart.com
"""
import datetime
import lxml.html
from urllib2 import urlopen
from math import ceil
from SharedFunctionsLib import *

con = get_db_connection()


def scrape_sp500_symbols():
    """
    Scrape S&P500 symbols from Wikipedia page
    :return: List of current SP500 symbols
    """
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
        # The first value (2) represents the status id, which is set to live by default
        ticker_symbols.append((2, sd['ticker'], sd['name'],
                               sd['sector'], timestamp, timestamp))

    return ticker_symbols


def filter_symbols(symbols):
    """
    If we are updating our symbols table, we do not want to
    add duplicate symbols, so here we filter out companies
    that already exist in the database.
    :param symbols: The list of symbols scraped from Wikipedia
    :return: List of symbols not yet represented in database
    """
    new_symbols = []
    unique_symbols = set()

    # Attempt to get any existing ticker data
    data = retrieve_db_tickers(con)

    # Collect a set of existing tickers
    for symbol in data:
        unique_symbols.add(symbol[1])

    # Now add any additional symbols not yet included in the
    # database from the SP500 wiki page
    for s in symbols:
        if s[1] not in unique_symbols:
            print(str(s[2]) + " will be added to the database!")
            new_symbols.append(s)

    return new_symbols


def insert_sp500_symbols(symbols):
    """
    Insert any new S&P500 symbols (that do not already belong)
    into the MySQL database.
    :param symbols: List of tuples where each tuple is data for a specific company
    """
    # Create the insert query
    column_fields = "status_id, ticker, name, sector, created_date, last_updated_date"
    insert_fields = ("%s, " * 6)[:-2]
    query_string = "INSERT INTO symbol (%s) VALUES (%s)" % (column_fields, insert_fields)

    # Insert symbol data into the database for every symbol
    with con:
        cur = con.cursor()
        # This line avoids the MySQL MAX_PACKET_SIZE
        # It chunks the inserts into sets of 100 at a time
        for i in range(0, int(ceil(len(symbols) / 100.0))):
            cur.executemany(query_string, symbols[i * 100:(i + 1) * 100 - 1])


if __name__ == "__main__":
    # 1.Scrape ticker data for the current companies existing in the S&P500 index from Wikipedia
    symbols = scrape_sp500_symbols()

    # 2.Filter out pre-existing data that may already belong in our database
    filtered_symbols = filter_symbols(symbols)

    # 3.Insert company ticker data into our MySQL database
    insert_sp500_symbols(filtered_symbols)

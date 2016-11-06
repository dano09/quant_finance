#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
from DAO import DAO
import pandas as pd
import MySQLdb as mdb


class MovingAverageCrossDAO(DAO):
    """
    Requires:
    host
    user
    password
    name
    """

    def __init__(self, host, user, password, name):
        self.host = host
        self.user = user
        self.password = password
        self.name = name
        self.con = self.get_db_connection()

    def get_db_connection(self):
        """
        Utility method that provides database credentials
        :return: MySQL Server database connection
        """
        return mdb.connect(self.host, self.user, self.password, self.name)

    def read_tickers(self):
        """
        TODO: Need to determine what companies to get, and how many
        :return:
        """
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT id, ticker FROM symbol where id = 2 or id = 5 or id = 7")
            data = cur.fetchall()
            return [(d[0], d[1]) for d in data]

    def read_data(self, ticker, start, end):
        with self.con:
            cur = self.con.cursor()
            # First query is to retrieve the id for the given symbol
            cur.execute("SELECT id FROM symbol WHERE ticker = %s", [ticker])
            ticker_id = cur.fetchall()
            ticker_id = ticker_id[0][0]

            # Second query gathers OHLCAV data
            cur.execute("SELECT * FROM cleaned_price "
                        "WHERE symbol_id = %s AND price_date >= %s AND price_date <= %s", (ticker_id, start, end))

            # Return none if no data exists for the ticker within the specified
            # time frame, otherwise return a dataframe with the OHLCAV data
            if not cur.rowcount:
                print "No price data available for " + ticker + " on " + str(start)
                price_data = None
            else:
                price_data = pd.DataFrame(list(cur.fetchall()))
                price_data.columns = ['id', 'symbol_id', 'price_date', 'created_date',
                                    'last_updated_date', 'open_price', 'high_price', 'low_price', 'close_price',
                                    'adj_close_price', 'volume']

            return price_data

    def write_data(self):
        print "test write"



#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
from DAO import DAO
import pandas as pd
import MySQLdb as mdb
import datetime
import traceback
import sys



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

    def validate_date(self, date):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT * FROM cleaned_price where price_date = %s", [date])
            data = cur.fetchall()
            return data

    def get_universe(self, start, end):
        """
        TODO: Need to determine what companies to get, and how many
        :return:
        """
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT ticker FROM symbol where first_price_date <= %s", [start])
            data = cur.fetchall()
            return [d[0] for d in data]

    def save_universe_by_volume(self, universe_by_volume):
        with self.con:
            universe_by_volume.to_sql(con=self.con, name='universe_by_volume', if_exists='append', index=False, flavor='mysql')

    def read_universe_by_volume(self):
        return pd.read_sql("SELECT * from universe_by_volume", con=self.con)

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

    def write_data(self, data):
        meta_id = self.save_maco_meta(data)
        return meta_id

    def save_maco_meta(self, data):
        timestamp = datetime.datetime.now()
        data.append(timestamp)
        # Build the parametrized query string
        column_str = """ticker_1, ticker_2, ticker_3, ticker_4, start_date, end_date, short_mavg,
        long_mavg, start_capital, universe_type, trades, end_capital, created_date"""

        insert_str = ("%s, " * 13)[:-2]
        query_string = "INSERT INTO maco (%s) VALUES (%s)" % (column_str, insert_str)

        # Connect with MySQL database and perform the insert query
        with self.con:
            cur = self.con.cursor()
            cur.executemany(query_string, [data])
            return cur.lastrowid

        #TODO: use to_SQL
        #with self.con:
        #    data.to_sql(con=self.con, name='maco', if_exists='append', index=False, flavor='mysql')

    def read_maco_meta(self, universe):
        try:
            sql = "SELECT * FROM maco WHERE universe_type = %(universe_type)s"
            columns = ['id', 'ticker_1', 'ticker_2', 'ticker_3', 'ticker_4',
                        'created_date', 'start_date', 'end_date',
                        'short_mavg', 'long_mavg', 'universe_type',
                        'trades' 'start_capital', 'end_capital']

            results = pd.read_sql(sql, self.con, params={"universe_type": universe}, columns=columns)

        except Exception as e:
            print "Could not download data"
            print "E: " + str(e)
            print(traceback.format_exception(*sys.exc_info()))

        return results

    def save_signals(self, signals, ticker, maco_id):
        timestamp = datetime.date.today()
        signals['maco_id'] = maco_id
        signals['ticker'] = ticker
        signals['created_date'] = timestamp
        signals['price_date'] = signals.index

        # Remove any data rows that include nan
        signals = signals.dropna()
        with self.con:
            signals.to_sql(con=self.con, name='maco_signals', if_exists='append', index=False, flavor='mysql')

    def read_maco_signals(self, maco_id, ticker_name):
        try:
            sql = "SELECT * FROM maco_signals WHERE maco_id = %(maco_id)s and ticker = %(ticker)s"
            results = pd.read_sql(sql, self.con, params={"maco_id": maco_id, "ticker": ticker_name})

        except Exception as e:
            print "Could not download data for maco_id = " + str(maco_id) + " and ticker name = " + str(ticker_name)
            print(traceback.format_exception(*sys.exc_info()))

        return results

    def save_maco_backtest(self, data, maco_id):
        timestamp = datetime.datetime.now()
        data['maco_id'] = maco_id
        data['created_date'] = timestamp
        data['price_date'] = data.index

        # Database columns are not ticker specific
        data = data.rename(index=str, columns={data.columns[0]: "ticker_1", data.columns[1]: "ticker_2", data.columns[2]: "ticker_3", data.columns[3]: "ticker_4"})
        # Remove any data rows that include nan
        clean_data = data.dropna()
        with self.con:
            clean_data.to_sql(con=self.con, name='maco_backtest', if_exists='append', index=False, flavor='mysql')

    def read_maco_backtest(self, maco_id):
        try:
            sql = "SELECT * FROM maco_backtest WHERE maco_id = %(maco_id)s "
            results = pd.read_sql(sql, self.con, params={"maco_id": maco_id})

        except Exception as e:
            print "Could not retrieve maco_backtest for maco_id = " + str(maco_id)
            print(traceback.format_exception(*sys.exc_info()))

        return results





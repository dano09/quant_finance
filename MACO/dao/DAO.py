#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Justin Dano 10/23/2016

from abc import ABCMeta, abstractmethod


class DAO(object):
    """
    Abstract Base class for a Data Access Object. This class will handle
    retrieving data from the database and writing results to the database.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_db_connection(self):
        """Provides logic to connect to database"""
        raise NotImplementedError("Must implement get_db_connections()!")

    @abstractmethod
    def read_tickers(self):
        """Provides logic needed to retrieve Ticker data from the database"""
        raise NotImplementedError("Must implement read_tickers()!")

    @abstractmethod
    def read_data(self, ticker, start, end):
        """Provides logic needed to retrieve a Dataframe object from the database"""
        raise NotImplementedError("Must implement read_data()!")

    @abstractmethod
    def write_data(self, data, flag):
        """Provides logic to write a Dataframe object to the database"""
        raise NotImplementedError("Must implement write_data()!")
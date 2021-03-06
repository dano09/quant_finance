#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Justin Dano 11/11/2016


from abc import ABCMeta, abstractmethod


class Table(object):
    """
    Abstract Base class for creating tables with Matplotlib
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def create_cell_text(self, b_dates, s_dates):
        """Assign data to each cell in a table"""
        raise NotImplementedError("Must implement create_cell_text()!")

    @abstractmethod
    def create_row_labels(self, data):
        """"""
        raise NotImplementedError("Must implement create_row_labels()!")

    @abstractmethod
    def create_table_colors(self, rows, num_of_columns, table_data):
        """"""
        raise NotImplementedError("Must implement create_table_colors()!")

    @abstractmethod
    def create_table(self, data):
        """"""
        raise NotImplementedError("Must implement create_table()!")


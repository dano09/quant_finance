#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
from Plotter import Plotter
from Table import Table
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.dates as md


class PlotResults(Plotter, Table):
    def __init__(self, small_backtest, large_backtest, trades):
        self.s_backtest = small_backtest
        self.l_backtest = large_backtest
        self.s_trades = trades[0]
        self.l_trades = trades[1]

    @staticmethod
    def setup_figure(self):
        """
        Creates and formats time-series graph
        :param number_of_events: Int - Used for determining height of the figure
        :return: The figure
        """
        fig = plt.figure(figsize=(12, 5))
        fig.patch.set_facecolor('silver')
        fig.suptitle(
            'Large vs Small Volume Portfolio Returns using the Moving Average CrossOver Strategy',
            fontsize=14, fontweight='bold')
        ax = fig.add_subplot(211)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time')
        ax.set_ylabel('Portfolio value in $ (USD)')
        return ax

    @staticmethod
    def get_data(self):
        return self.s_backtest['total'], self.l_backtest['total']

    @staticmethod
    def plot_data(self, ax, data):
        ax.plot(data[0], 'navy', lw=2.5)
        ax.plot(data[1], 'c', lw=2.5)
        ax.legend(['Small Volume Portfolio', 'Large Volume Portfolio'], loc=2, prop={'size': 7})


    def calculate_annualized_return(self, starting_cap, ending_cap, years):
        return (((ending_cap - starting_cap) / starting_cap) / years) * 100

    def create_row(self, backtest, trades):
        row = []
        starting_cap = backtest.iloc[0]['total']
        ending_cap = backtest.iloc[-1]['total']

        start_date = backtest.iloc[0]['price_date']
        end_date = backtest.iloc[-1]['price_date']

        difference_in_years = relativedelta(end_date, start_date).years
        annualized_return = self.calculate_annualized_return(starting_cap, ending_cap, difference_in_years)

        row.append("$ " + str(starting_cap))
        row.append(trades)
        row.append("$ " + str(ending_cap))
        row.append("%.3f" % annualized_return + "%")
        return row

    def create_cell_text(self, events=None, event_dates=None, b_dates=None, s_dates=None):
        small_vol_row = self.create_row(self.s_backtest, self.s_trades)
        large_vol_row = self.create_row(self.l_backtest, self.l_trades)
        return small_vol_row, large_vol_row

    def create_row_labels(self):
        row1 = 'Low-Vol Portfolio'
        row2 = 'High-Vol Portfolio'
        return row1, row2

    def create_table_colors(self, row_labels, column_labels, cell_text):
        cell_colors = []
        cell_color = ['lightgreen'] * len(column_labels)
        cell_color2 = ['lightcoral'] * len(column_labels)
        col_colors = ['beige'] * len(column_labels)
        row_colors = ['beige'] * len(row_labels)

        # Two rows for this table
        cell_colors.append(cell_color)
        cell_colors.append(cell_color2)

        return [cell_colors, row_colors, col_colors]

    @staticmethod
    def create_table(self, data=None):

        cell_text = self.create_cell_text(self)

        row_labels = self.create_row_labels()

        column_labels = ['Starting Capital', 'Number of Trades', 'Ending Capital', 'Annualized Return']

        colors = self.create_table_colors(row_labels, column_labels, cell_text)

        table = plt.table(cellText=cell_text, cellColours=colors[0],
                          rowColours=colors[1], rowLabels=row_labels,
                          colColours=colors[2], colLabels=column_labels,
                          bbox=[0.0, -1.35, 1.0, 1.0],
                          cellLoc='center')


        table.set_fontsize(8)
        return table

    def plot_results(self):
        ax = self.setup_figure(self)
        portfolio_returns = self.get_data(self)
        self.plot_data(self, ax, portfolio_returns)

        self.create_table(self)



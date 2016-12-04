#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

from MACO.maco_display.Plotter import Plotter
from MACO.maco_display.Table import Table


class PlotResults(Plotter, Table):
    def __init__(self, small_backtest, large_backtest, trades):
        self.s_backtest = small_backtest
        self.l_backtest = large_backtest
        self.s_trades = trades[0]
        self.l_trades = trades[1]

    def setup_figure(self, event_count=None):
        """
        Creates and formats time-series graph comparing low and high volume portfolios
        """
        fig = plt.figure(figsize=(8, 5))
        fig.patch.set_facecolor('silver')
        fig.suptitle(
            'Comparing High and Low Volume Portfolios ',
            fontsize=14, fontweight='bold')
        ax = fig.add_subplot(211)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time')
        ax.set_ylabel('Portfolio value in $ (USD)')
        return ax

    def get_data(self):
        return self.s_backtest['total'], self.l_backtest['total']

    def plot_data(self, ax, data, plot_type=None):
        ax.plot(data[0], 'navy', lw=2.5)
        ax.plot(data[1], 'c', lw=2.5)
        ax.axhline(y=100000, linewidth=2, color='k')
        ax.legend(['Small Volume Portfolio', 'Large Volume Portfolio'], loc=2, prop={'size': 10})

    def calculate_annualized_return(self, s_cap, e_cap, years):
        return (((e_cap - s_cap) / s_cap) / years) * 100

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

    def create_cell_text(self, b_dates=None, s_dates=None):
        small_vol_row = self.create_row(self.s_backtest, self.s_trades)
        large_vol_row = self.create_row(self.l_backtest, self.l_trades)
        return small_vol_row, large_vol_row

    def create_row_labels(self, data=None):
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

        table.set_fontsize(60)
        return table

    def plot_results(self):
        """
        Plot both low-volume and high-volume portfolios for comparison. Also include
        portfolio table to identify some key parameters, indicators, and results for each portfolio.
        """
        ax = self.setup_figure()
        portfolio_returns = self.get_data()
        self.plot_data(ax, portfolio_returns)
        self.create_table()



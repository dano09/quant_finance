#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
import matplotlib.pyplot as plt

from MACO.maco_display.Plotter import Plotter
from MACO.maco_display.Table import Table


class PlotStrategy(Plotter, Table):

    def __init__(self, security):
        self.security = security
        self.data = self.get_data()

    def get_data(self):
        """
        Determine the x and y coordinates for signals to buy or sell stock.
        The x-axis are Dates, and Y-axis is the value of the moving averages
        :return [List, List, List, List]
        """
        security = self.security

        # Determine the dates for each signal generated from MACO strategy
        buy_dates = self.security.signals.ix[self.security.signals.positions == 1.0].index
        sell_dates = security.signals.ix[security.signals.positions == -1.0].index

        # Determine the price of the stock on the days the MACO strategy identified
        # a trade signal
        mavg_buy_signal = security.signals.short_mavg[security.signals.positions == 1.0]
        mavg_sell_signal = security.signals.short_mavg[security.signals.positions == -1.0]

        return [buy_dates, mavg_buy_signal, sell_dates, mavg_sell_signal]

    def setup_figure(self, signal_count):
        """
        Creates and formats figure that contains a time-series graph and table
        """
        # Dynamically adjust height of figure based on number of signals. This is to accommodate for
        # the different number of signals that populate the table for different figures.
        # Used for styling purposes
        size = (signal_count / 4) + 5

        fig = plt.figure(figsize=(8, size))
        fig.patch.set_facecolor('silver')
        fig.suptitle('Moving Average Crossover for ' + self.security.symbol, fontsize=14, fontweight='bold')
        ax = fig.add_subplot(211)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time Horizon of Backtest')
        ax.set_ylabel('Price in $ (USD)')
        return ax

    def setup_graph(self):
        """
        Creates and formats figure that contains a time-series graph and table
        """
        # Dynamically adjust height of figure based on number of signals. This is to accommodate for
        # the different number of signals that populate the table for different figures.
        # Used for styling purposes

        fig = plt.figure(figsize=(8, 10))
        #fig.patch.set_facecolor('silver')
        fig.suptitle('Moving Average Crossover for ' + self.security.symbol, fontsize=14, fontweight='bold')
        ax = fig.add_subplot(111)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time Horizon of Backtest')
        ax.set_ylabel('Price in $ (USD)')
        return ax

    def plot_data(self, ax, data, plot_type=None):
        """
        Plot closing price, moving averages, and signals
        :param self: MarketOnCloseSecurity
        :param ax: Figure
        :param data: List of (Date,Price) coordinates
        """
        # Plot price and Moving Averages
        ax.plot(self.security.bars['adj_close_price'].astype(float), color='navy', lw=2.5)
        ax.plot(self.security.signals['short_mavg'], 'dodgerblue', lw=2.)
        ax.plot(self.security.signals['long_mavg'], 'sandybrown', lw=2.)
        #ax.legend(['Closing Price', 'Short MAVG', 'Long MVAG'], loc=2, prop={'size': 10})

        # Plot Buy Signals
        ax.plot(data[0], data[1], '^', markersize=10, color='lightgreen')
        # Plot Sell Signals
        ax.plot(data[2], data[3], 'v', markersize=10, color='lightcoral')
        ax.legend(['Closing Price', 'Short MAVG', 'Long MVAG', 'Buy', 'Sell'], numpoints=1, loc=2, prop={'size': 10})


    def create_cell_text(self, b_dates, s_dates):
        """
        Generates the data to be put in each cell of the table
        :param b_dates: [Datetime] - Dates of buy signals
        :param s_dates: [Datetime] - Dates of sell signals
        :return: All the rows for the table sorted by date of event
        """
        prices = self.security.bars
        table = []
        # Generate Buy Rows
        for v in b_dates.values:
            table_entry = [v.strftime("%Y-%m-%d"), "Buy", "%.4f" % prices.at[v, 'adj_close_price']]
            table.append(table_entry)

        # Generate Sell Rows
        for v in s_dates.values:
            table_entry = [v.strftime("%Y-%m-%d"), "Sell", "%.4f" % prices.at[v, 'adj_close_price']]
            table.append(table_entry)

        return sorted(table)

    def create_row_labels(self, data):
        row_labels = []
        for i, v in enumerate(data):
            row_labels.append(str(i + 1))
        return row_labels

    def create_table_colors(self, rows, num_of_columns=None, table_data=None):
        cell_colors = []
        buy_color = ['aliceblue'] * 3
        sell_color = ['aliceblue'] * 3
        col_colors = ['beige'] * 3
        row_colors = ['beige'] * len(rows)

        for i in rows:
            if int(i) % 2 == 0:
                cell_colors.append(sell_color)
            else:
                cell_colors.append(buy_color)

        return [cell_colors, row_colors, col_colors]

    def create_table(self, data, event=None, event_dates=None):
        cell_text = self.create_cell_text(data[0], data[2])
        row_labels = self.create_row_labels(cell_text)
        col_labels = ['Date', 'Signal', 'Price']
        colors = self.create_table_colors(row_labels)

        plt.table(cellText=cell_text, cellColours=colors[0],
                  rowColours=colors[1], rowLabels=row_labels,
                  colColours=colors[2], colLabels=col_labels,
                  bbox=[0.0, -1.3, 1.0, 1.0], cellLoc='center')

    def get_total_events(self):
        return len(self.data[0]) + len(self.data[0])

    def plot_price_with_signals(self):
        """
        Displays the signals generated from the Moving Average Crossover Strategy.
        The first figure is a time series, containing signal positions with the closing price
        and moving average curves. While the second figure is the table detailing the specific
        price that stock was bought or sold based on a signal
        """
        events = self.get_total_events()
        ax = self.setup_figure(events)
        data = self.get_data()
        self.plot_data(ax, data)
        self.create_table(data)
        plt.show()


    def plot_large_number_of_signals(self):
        """
        Displays the signals generated from the Moving Average Crossover Strategy.
        The first figure is a time series, containing signal positions with the closing price
        and moving average curves. While the second figure is the table detailing the specific
        price that stock was bought or sold based on a signal
        """
        ax = self.setup_graph()
        data = self.get_data()
        self.plot_data(ax, data)
        plt.show()


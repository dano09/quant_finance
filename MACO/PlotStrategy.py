#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
from Plotter import Plotter
from Table import Table
import matplotlib.pyplot as plt


class PlotStrategy(Plotter, Table):

    def __init__(self, security):
        self.security = security
        self.data = self.get_data(self)

    @staticmethod
    def get_data(self):
        """
        Determine the x and y coordinates for signals to buy or sell stock.
        The x-axis are Dates, and Y-axis is the value of the moving averages
        :return: List of lists
        """
        security = self.security

        buy_dates = self.security.signals.ix[self.security.signals.positions == 1.0].index
        mavg_buy_signal = security.signals.short_mavg[security.signals.positions == 1.0]

        sell_dates = security.signals.ix[security.signals.positions == -1.0].index
        mavg_sell_signal = security.signals.short_mavg[security.signals.positions == -1.0]

        return [buy_dates, mavg_buy_signal, sell_dates, mavg_sell_signal]

    @staticmethod
    def setup_figure(self, count):
        """
        Creates and formats time-series graph
        :return: The figure
        """
        size = (count / 4) + 5

        fig = plt.figure(figsize=(10, size))
        fig.patch.set_facecolor('silver')
        fig.suptitle('Moving Average Crossover for ' + self.security.symbol, fontsize=14, fontweight='bold')
        ax = fig.add_subplot(211)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time Horizon of Backtest')
        ax.set_ylabel('Price in $ (USD)')
        return ax


    @staticmethod
    def plot_data(self, ax, data):
        """
        Plot closing price, moving averages, and signals
        :param self: MarketOnCloseSecurity
        :param ax: Figure
        :param data: List of (Date,Price) Coordinates
        """
        ax.plot(self.security.bars['close_price'].astype(float), color='navy', lw=2.5)
        ax.plot(self.security.signals['short_mavg'], 'dodgerblue', lw=2.)
        ax.plot(self.security.signals['long_mavg'], 'sandybrown', lw=2.)
        ax.legend(['Closing Price', 'Short MAVG', 'Long MVAG'], prop={'size': 7})
        # Plot Buy Signals
        ax.plot(data[0], data[1], '^', markersize=10, color='lightgreen')
        # Plot Sell Signals
        ax.plot(data[2], data[3], 'v', markersize=10, color='lightcoral')

    @staticmethod
    def create_cell_text(self, b_dates, s_dates, events=None, event_dates=None):
        """
        Generate Cell data for table
        """
        prices = self.security.bars
        table = []
        # Generate Buy Rows
        for v in b_dates.values:
            table_entry = [v.strftime("%Y-%m-%d"), "Buy", "%.4f" % prices.at[v, 'close_price']]
            table.append(table_entry)

        # Generate Sell Rows
        for v in s_dates.values:
            table_entry = [v.strftime("%Y-%m-%d"), "Sell", "%.4f" % prices.at[v, 'close_price']]
            table.append(table_entry)

        # Return rows sorted by date
        return sorted(table)

    @staticmethod
    def create_row_labels(data):
        row_labels = []
        for i, v in enumerate(data):
            row_labels.append(str(i + 1))
        return row_labels

    @staticmethod
    def create_table_colors(self, rows, num_of_columns=None, table_data=None):
        cell_colors = []
        buy_color = ['lightgreen'] * 3
        sell_color = ['lightcoral'] * 3
        col_colors = ['beige'] * 3
        row_colors = ['beige'] * len(rows)

        for i in rows:
            if int(i) % 2 == 0:
                cell_colors.append(sell_color)
            else:
                cell_colors.append(buy_color)

        return [cell_colors, row_colors, col_colors]

    @staticmethod
    def create_table(self, data, event=None, event_dates=None):
        cell_text = self.create_cell_text(self, data[0], data[2])
        row_labels = self.create_row_labels(cell_text)
        col_labels = ['Date', 'Signal', 'Price']
        colors = self.create_table_colors(self, row_labels)

        plt.table(cellText=cell_text, cellColours=colors[0],
                  rowColours=colors[1], rowLabels=row_labels,
                  colColours=colors[2], colLabels=col_labels,
                  bbox=[0.0, -1.3, 1.0, 1.0], cellLoc='center')

    def get_total_events(self):
        return len(self.data[0]) + len(self.data[0])


    def plot_price_with_signals(self):
        """
        Plots each security on a separate figure
        :return:
        """
        events = self.get_total_events()
        ax = self.setup_figure(self, events)
        data = self.get_data(self)
        self.plot_data(self, ax, data)
        self.create_table(self, data)
        plt.show()





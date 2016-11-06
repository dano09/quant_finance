#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.table import Table

class Plotter:

    def __init__(self, portfolio, returns):
        self.portfolio = portfolio
        self.securities = portfolio.market_on_close_securities
        self.returns = returns

    @staticmethod
    def setup_figure(symbol):
        fig = plt.figure()
        fig.patch.set_facecolor('silver')
        fig.suptitle('Moving Average Crossover for ' + symbol, fontsize=14, fontweight='bold')
        ax = fig.add_subplot(211)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time')
        ax.set_ylabel('Price in $ (USD)')
        return ax

    @staticmethod
    def get_data(security):
        buy_dates = security.signals.ix[security.signals.positions == 1.0].index
        buy_prices = security.signals.short_mavg[security.signals.positions == 1.0]
        sell_dates = security.signals.ix[security.signals.positions == -1.0].index
        sell_prices = security.signals.short_mavg[security.signals.positions == -1.0]

        return [buy_dates, buy_prices, sell_dates, sell_prices]

    @staticmethod
    def plot_data(ax, security, data):
        ax.plot(security.bars['close_price'].astype(float), color='navy', lw=2.5)
        ax.plot(security.signals['short_mavg'], 'dodgerblue', lw=2.)
        ax.plot(security.signals['long_mavg'], 'sandybrown', lw=2.)
        ax.legend(['Closing Price', 'Short MAVG', 'Long MVAG'])
        ax.plot(data[0], data[1], '^', markersize=15, color='lightgreen')
        ax.plot(data[2], data[3], 'v', markersize=15, color='lightcoral')

    @staticmethod
    def create_cell_text(b_dates, b_prices, s_dates, s_prices):
        table = []
        for v in b_dates.values:
            table_entry = [v.strftime("%Y-%m-%d"), "Buy", "%.4f" % b_prices[v]]

            table.append(table_entry)

        for v in s_dates.values:
            table_entry = [v.strftime("%Y-%m-%d"), "Sell", "%.4f" % s_prices[v]]
            table.append(table_entry)

        return sorted(table)

    @staticmethod
    def create_row_labels(data):
        row_labels = []
        for i, v in enumerate(data):
            row_labels.append(str(i + 1))
        return row_labels

    @staticmethod
    def set_table_colors(rows):
        buy_color = ['lightgreen'] * 3
        sell_color = ['lightcoral'] * 3
        col_colors = ['beige'] * 3
        row_colors = ['beige'] * len(rows)

        cell_colors = []
        for i in rows:
            if int(i) % 2 == 0:
                cell_colors.append(sell_color)
            else:
                cell_colors.append(buy_color)

        return [cell_colors, row_colors, col_colors]

    @staticmethod
    def create_table(self, data):
        cell_text = self.create_cell_text(data[0], data[1], data[2], data[3])
        row_labels = self.create_row_labels(cell_text)
        col_labels = ['Date', 'Signal', 'Price']
        colors = self.set_table_colors(row_labels)

        plt.table(cellText=cell_text, cellColours=colors[0],
                  rowColours=colors[1], rowLabels=row_labels,
                  colColours=colors[2], colLabels=col_labels,
                  bbox=[0.0, -1.3, 1.0, 1.0], cellLoc='center')

    def plot_price_with_signals(self):
        """
        Plots each security on a separate figure
        :return:
        """
        for security in self.securities:
            ax = self.setup_figure(security.symbol)
            price_data = self.get_data(security)
            self.plot_data(ax, security, price_data)
            self.create_table(price_data)

    def plot_price_with_signals_grouped(self):
        """
        Plots 4 securities on a single portfolio
        :return:
        """
        #TODO: Add Asset to only allow securities in groups of 4




    def p_get_data(self, ):
        pass


    def p_create_cell_text(self, b_dates, b_prices, s_dates, s_prices):
        pass

    def p_create_row_labels(self, data):
        pass

    def p_set_table_colors(self, rows):
        pass

    def p_create_table(self, data):
        cell_text = self.create_cell_text(data[0], data[1], data[2], data[3])
        row_labels = self.create_row_labels(cell_text)
        col_labels = ['Date', 'Event', 'Price']
        colors = self.set_table_colors(row_labels)

        plt.table(cellText=cell_text, cellColours=colors[0],
                  rowColours=colors[1], rowLabels=row_labels,
                  colColours=colors[2], colLabels=col_labels,
                  bbox=[0.0, -1.3, 1.0, 1.0], cellLoc='center')

    def plot_equity_curve(self):
        """
        Plot the equity curve of the portfolio
        #TODO: Currently only handles signals for one ticker - need to modify to handle more
        :return:
        """
        fig = plt.figure()
        # Plot the equity curve in dollars
        ax = fig.add_subplot(211, ylabel='Portfolio value in $')
        self.returns['total'].plot(ax=ax, lw=2.)

        colors = plt.cm.plasma(np.linspace(0, 1, len(self.securities)))
        # Plot the "buy" and "sell" trades against the equity curve
        tickers = []
        ticker_and_dates = {}
        row_length = 0
        for i, security in enumerate(self.securities):
            tickers.append(security.symbol)
            buy_date = self.returns.ix[security.signals.positions == 1.0].index
            total_at_buy = self.returns.total[security.signals.positions == 1.0]
            sell_date = self.returns.ix[security.signals.positions == -1.0].index
            total_at_sell = self.returns.total[security.signals.positions == -1.0]

            buy_tuple = ('b', buy_date.values)
            sell_tuple = ('s', sell_date.values)

            ax.plot(buy_date, total_at_buy, '^', markersize=10, color=colors[i], label=str(security.symbol))
            ax.plot(sell_date, total_at_sell, 'v', markersize=10, color=colors[i], label='_nolegend_')
            row_length += len(buy_date.values) + len(sell_date.values)
            print "row_length is:"
            print row_length
            ticker_and_dates[security.symbol] = (buy_tuple, sell_tuple)

        plt.legend(numpoints=1)
        print "ticker_and_dates"
        print ticker_and_dates
        column_values = ['Date', 'Signal', 'Holdings', 'Cash', 'Total', 'Return']
        column_values[2:2] = tickers
        print "self.returns"
        print self.returns


        #static_labels = ['Date', 'Signal', 'ABT', 'ATVI', 'ADBE', 'Holdings', 'Cash', 'Total', 'Return']
        self.p_create_table([buy_date, total_at_buy, sell_date, total_at_sell])

        fig.show()
        print "test"



#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
import matplotlib.pyplot as plt
import numpy as np
from dateutil.parser import parse
import pandas as pd
from matplotlib.table import Table

class Plotter:

    def __init__(self, portfolio, returns):
        self.portfolio = portfolio
        self.securities = portfolio.market_on_close_securities
        self.returns = returns

    @staticmethod
    def setup_figure(symbol):
        """
        Creates and formats time-series graph
        :param symbol: String - Ticker used for time-series
        :return: The figure
        """
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
        """
        Determine the x and y cordinates for signals to buy or sell stock.
        The x-axis are Dates, and Y-axis is the value of the moving averages
        :param security: MarketOnCloseSecurity - used to i
        :return: List of lists
        """
        buy_dates = security.signals.ix[security.signals.positions == 1.0].index
        mavg_buy_signal = security.signals.short_mavg[security.signals.positions == 1.0]
        sell_dates = security.signals.ix[security.signals.positions == -1.0].index
        mavg_sell_signal = security.signals.short_mavg[security.signals.positions == -1.0]


        return [buy_dates, mavg_buy_signal, sell_dates, mavg_sell_signal]

    @staticmethod
    def plot_data(ax, security, data):
        """
        Plot closing price, moving averages, and signals
        :param ax: Figure
        :param security: MarketOnCloseSecurity
        :param data: List of (Date,Price) Coordinates
        """
        ax.plot(security.bars['close_price'].astype(float), color='navy', lw=2.5)
        ax.plot(security.signals['short_mavg'], 'dodgerblue', lw=2.)
        ax.plot(security.signals['long_mavg'], 'sandybrown', lw=2.)
        ax.legend(['Closing Price', 'Short MAVG', 'Long MVAG'])
        # Plot Buy Signals
        ax.plot(data[0], data[1], '^', markersize=15, color='lightgreen')
        # Plot Sell Signals
        ax.plot(data[2], data[3], 'v', markersize=15, color='lightcoral')

    @staticmethod
    def create_cell_text(prices, b_dates, s_dates):
        """
        Generate Cell data for table
        """
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

    def create_table(self, security, data):
        cell_text = self.create_cell_text(security.bars, data[0], data[2])
        row_labels = self.create_row_labels(cell_text)
        col_labels = ['Date', 'Signal', 'Price']
        colors = self.set_table_colors(row_labels)

        plt.table(cellText=cell_text, cellColours=colors[0],
                  rowColours=colors[1], rowLabels=row_labels,
                  colColours=colors[2], colLabels=col_labels,
                  bbox=[0.0, -1.3, 1.0, 1.0], cellLoc='center')
        #plt.show()

    def plot_price_with_signals(self):
        """
        Plots each security on a separate figure
        :return:
        """
        for security in self.securities:
            ax = self.setup_figure(security.symbol)
            price_data = self.get_data(security)
            self.plot_data(ax, security, price_data)
            self.create_table(security, price_data)

        plt.show()

    def plot_price_with_signals_grouped(self):
        """
        Plots 4 securities on a single portfolio
        :return:
        """
        #TODO: Add Asset to only allow securities in groups of 4



    @staticmethod
    def p_setup_figure():
        """
        Creates and formats time-series graph
        :param symbol: String - Ticker used for time-series
        :return: The figure
        """
        fig = plt.figure(figsize=(15, 6))
        fig.patch.set_facecolor('silver')
        fig.suptitle('Portfolio snapshots', fontsize=14, fontweight='bold')
        ax = fig.add_subplot(211)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time')
        ax.set_ylabel('Portfolio value in $ (USD)')
        return ax

    def p_get_data(self, stock):
        buy_date = self.returns.ix[stock.signals.positions == 1.0].index
        portfolio_at_buy = self.returns.total[stock.signals.positions == 1.0]
        sell_date = self.returns.ix[stock.signals.positions == -1.0].index
        portfolio_at_sell = self.returns.total[stock.signals.positions == -1.0]

        return [buy_date, portfolio_at_buy, sell_date, portfolio_at_sell]


    def p_create_cell_text(self, events, dates, portfolio):
        table = []
        for d in dates:
            row = [d.strftime("%Y-%m-%d")]
            row.append(events[d.strftime("%Y-%m-%d")])

            portfolio_rows = portfolio.ix[d].values[:-1]
            print "portfolio_rows type:"
            print type(portfolio_rows)
            print "port rows"
            print portfolio_rows

            row.extend("{0:.2f}".format(val) for val in portfolio.ix[d].values[:-1])
            table.append(row)

        return table

    @staticmethod
    def p_create_row_labels(num_of_rows):
        rows = []
        for i in range(num_of_rows):
            rows.append(i)
        return rows

    def p_set_table_colors(self, rows, num_of_columns, table_data):
        cell_colors = []
        print "table data:"
        print table_data
        #print "columns is: "
        #print columns
        positive_returns = ['lightgreen'] * num_of_columns
        negative_returns = ['lightcoral'] * num_of_columns
        col_colors = ['beige'] * num_of_columns
        row_colors = ['beige'] * len(rows)

        #cell_colors = []
        # If we have positive returns for a specific day, color the table row green.
        # Otherwise make it red
        for day in table_data:
            if float(day[8]) >= self.portfolio.initial_capital:
                cell_colors.append(positive_returns)
            else:
                cell_colors.append(negative_returns)

        return [cell_colors, row_colors, col_colors]

    def p_create_table(self, events, dates, rows, columns, portfolio):
        """
        :param events: Dict - {Date:Event} where Event is a String identifying
        what event happened
        :param dates: List - Dates of events
        :param rows: Int - number of Dates (rows) to create for the table
        :param columns: List - Column headers
        :param portfolio: Dataframe - Portfolio with calculated totals and returns
        :return:
        """
        print "events are: "
        print events
        cell_text = self.p_create_cell_text(events, dates, portfolio)
        #cell_text.pop(0)
        row_labels = self.p_create_row_labels(rows)
        print "row_labels"
        print row_labels
        print "cell text"
        print cell_text
        #row_labels.pop(len(row_labels))
        colors = self.p_set_table_colors(row_labels, len(columns), cell_text)
        print "colors[0]"
        print colors[0]


        table = plt.table(cellText=cell_text, cellColours=colors[0],
                  rowColours=colors[1], rowLabels=row_labels,
                  colColours=colors[2], colLabels=columns,
                  bbox=[0.0, -1.3, 1.0, 1.0], cellLoc='center')
        #plt.table.set_fontsize(24)
        #plt.table.scale(2,2)
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(2, 2)

        cell_dict = table.get_celld()
        #print "celldict is:"
        #print cell_dict
        #for i in range(13):
        #    cell_dict[(i,1)].set_width(0.3)


    @staticmethod
    def create_event(date, signal, symbol, bars):
        price = bars.loc[date]['close_price']
        if signal is 'b':
            event = "B:" + symbol + " @ " + "%.2f" % price
        else:
            event = "S:" + symbol + " @ " + "%.2f" % price

        return event

    def plot_equity_curve(self):
        """
        Plot the equity curve of the portfolio
        #TODO: Currently only handles signals for one ticker - need to modify to handle more
        :return:
        """

        #fig = plt.figure(figsize=(15, 6))
        #figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
        # Plot the equity curve in dollars
        #ax = fig.add_subplot(211, ylabel='Portfolio value in $')
        ax = self.p_setup_figure()
        self.returns['total'].plot(ax=ax, lw=2.)

        colors = plt.cm.plasma(np.linspace(0, 1, len(self.securities)))
        # Plot the "buy" and "sell" trades against the equity curve
        tickers = []
        event_dates = []
        events = {}

        #FOR EACH SECURITY
        for i, security in enumerate(self.securities):
            tickers.append(security.symbol)
            data = self.p_get_data(security)

            # Create event string for each buy signal
            for date in data[0].values:
                if date not in event_dates:
                    event_dates.append(date)

                event = self.create_event(date, 'b', security.symbol, security.bars)
                self.add_event(date.strftime("%Y-%m-%d"), event, events)

            # Create event string for each sell signal
            for date in data[2].values:
                if date not in event_dates:
                    event_dates.append(date)

                event = self.create_event(date, 's', security.symbol, security.bars)
                self.add_event(date.strftime("%Y-%m-%d"), event, events)

            ax.plot(data[0], data[1], '^', markersize=10, color=colors[i], label=str(security.symbol))
            ax.plot(data[2], data[3], 'v', markersize=10, color=colors[i], label='_nolegend_')

        plt.legend(numpoints=1)
        column_values = ['Date', 'Event', 'Holdings', 'Cash', 'Total']
        column_values[2:2] = tickers

        self.p_create_table(events, sorted(event_dates), len(event_dates), column_values, self.returns)

        #fig.show()


    def add_event(self, date, event, events):
        # Create a new event
        if date not in events:
            events[date] = event

        # An event already exists for this date, so we add an additional one
        else:
            event_string = events.get(date)
            #e_s = event_string[0]
            event_string += '\n' + event
            #event_string.extend(event)

            events[date] = event_string



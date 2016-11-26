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

class PlotPortfolio(Plotter, Table):

    def __init__(self, portfolio, returns):
        self.portfolio = portfolio
        self.securities = portfolio.market_on_close_securities
        self.returns = returns
        self.tickers = [t.symbol for t in self.securities]
        #self.events, self.event_dates, self.event_count = self.generate_events(self)

    @staticmethod
    def create_event(date, signal, symbol, bars):
        price = bars.loc[date]['close_price']
        if signal is 'b':
            event = "B:" + symbol + " @ " + "%.2f" % price
        else:
            event = "S:" + symbol + " @ " + "%.2f" % price

        return event

    @staticmethod
    def add_event(date, event, events):
        # Create a new event
        if date not in events:
            events[date] = [event]

        # An event already exists for this date, so we add an additional one
        else:
            event_list = events.get(date)
            event_list.append(event)
            events[date] = event_list

    @staticmethod
    def generate_events(self, start_date, end_date):
        events = {start_date: ["Start Date"], end_date: ["End Date"]}
        #datetime.strptime('2014-12-04', '%Y-%m-%d').date()

        # Converting strings to datetime
        event_dates = [datetime.strptime(start_date, '%Y-%m-%d').date(),
                       datetime.strptime(end_date, '%Y-%m-%d').date()]

        event_count = 0

        # Create first and last event
        #events[start_date] = "Backtesting Begins"
        #events[end_date] = "Backtesting Ends"
        # FOR EACH SECURITY
        for i, security in enumerate(self.securities):
            data = self.get_data(self)

            # Create event string for each buy signal
            #for date in data[0].values:
            print data
            print "data[i]"
            print data[i]
            print "data[i][0]"
            print data[i][0]
            for date in data[i][0].values:
                if date not in event_dates:
                    event_dates.append(date)

                event = self.create_event(date, 'b', security.symbol, security.bars)
                self.add_event(date.strftime("%Y-%m-%d"), event, events)
                event_count += 1

            # Create event string for each sell signal
            for date in data[i][2].values:
                if date not in event_dates:
                    event_dates.append(date)

                event = self.create_event(date, 's', security.symbol, security.bars)
                self.add_event(date.strftime("%Y-%m-%d"), event, events)
                event_count += 1

        return events, event_dates, event_count

    @staticmethod
    def create_event(date, signal, symbol, bars):
        price = bars.loc[date]['close_price']
        if signal is 'b':
            event = "B:" + symbol + " @ " + "%.2f" % price
        else:
            event = "S:" + symbol + " @ " + "%.2f" % price

        return event

    @staticmethod
    def setup_figure(self, event_count):
        """
        Creates and formats time-series graph
        :param number_of_events: Int - Used for determining height of the figure
        :return: The figure
        """
        # Figure starts at a height of 4 inches and increments an inch every 4 events
        size = (event_count / 4) + 4
        fig = plt.figure(figsize=(15, size))
        fig.patch.set_facecolor('silver')
        fig.suptitle('Portfolio snapshots', fontsize=14, fontweight='bold')
        ax = fig.add_subplot(211)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time')
        ax.set_ylabel('Portfolio value in $ (USD)')
        return ax

    @staticmethod
    def get_data(self):
        portfolio_data = []
        for security in self.securities:
            security_data = [self.returns.ix[security.signals.positions == 1.0].index]
            security_data.append(self.returns.total[security.signals.positions == 1.0])
            security_data.append(self.returns.ix[security.signals.positions == -1.0].index)
            security_data.append(self.returns.total[security.signals.positions == -1.0])
            portfolio_data.append(security_data)

        return portfolio_data

    @staticmethod
    def plot_data(self, ax, data):
        self.returns['total'].plot(ax=ax, lw=2.)
        colors = plt.cm.plasma(np.linspace(0, 1, len(self.securities)))
        # FOR EACH SECURITY
        for i, security in enumerate(self.securities):
            ax.plot(data[i][0], data[i][1], '^', markersize=10, color=colors[i], label=str(security.symbol))
            ax.plot(data[i][2], data[i][3], 'v', markersize=10, color=colors[i], label='_nolegend_')

        plt.legend(numpoints=1)

    def print_full(x):
        pd.set_option('display.max_rows', len(x))
        print(x)
        pd.reset_option('display.max_rows')

    @staticmethod
    def create_cell_text(self, events, event_dates, b_dates=None, s_dates=None):

        table = []
        # Create a table row for each event
        for d in event_dates:
            event_list = events[d.strftime("%Y-%m-%d")]
            # Some dates have multiple events
            for e in event_list:
                row = [d.strftime("%Y-%m-%d")]
                row.append(e)
                #print "self.returns"
                #print self.returns
                #print "self.returns.ix[d]"
                #print self.returns.ix[d]
                #self.print_full(self.returns)
                #self.print_full(self.returns.ix[d])
                row.extend("{0:.2f}".format(val) for val in self.returns.ix[d].values[:-1])
                table.append(row)

        return sorted(table)

    @staticmethod
    def create_row_labels(num_of_rows):
        rows = []
        for i in range(num_of_rows):
            rows.append(i + 1)
        return rows

    @staticmethod
    def create_table_colors(self, rows, num_of_columns, table_data):
        cell_colors = []
        positive_returns = ['lightgreen'] * num_of_columns
        negative_returns = ['lightcoral'] * num_of_columns
        col_colors = ['beige'] * num_of_columns
        row_colors = ['beige'] * len(rows)

        # If we have positive returns for a specific day, color the table row green.
        # Otherwise make it red
        for day in table_data:
            if float(day[8]) >= self.portfolio.initial_capital:
                cell_colors.append(positive_returns)
            else:
                cell_colors.append(negative_returns)

        return [cell_colors, row_colors, col_colors]

    @staticmethod
    def create_table(self, events, event_dates, data=None):
        """
        :param events: Dict - {Date:Event} where Event is a String identifying
        what event happened
        :param dates: List - Dates of events
        :param rows: Int - number of Dates (rows) to create for the table
        :param columns: List - Column headers
        :param portfolio: Dataframe - Portfolio with calculated totals and returns
        :return:
        """
        cell_text = self.create_cell_text(self, events, event_dates)
        row_labels = self.create_row_labels(len(cell_text))

        column_labels = ['Date', 'Event', 'Holdings', 'Cash', 'Total']
        column_labels[2:2] = self.tickers

        colors = self.create_table_colors(self, row_labels, len(column_labels), cell_text)

        table = plt.table(cellText=cell_text, cellColours=colors[0],
                          rowColours=colors[1], rowLabels=row_labels,
                          colColours=colors[2], colLabels=column_labels,
                          bbox=[0.0, -1.3, 1.0, 1.0])

        table.auto_set_font_size(False)
        table.set_fontsize(9)

    def plot_equity_curve(self, start_date, end_date):
        """
        Plot the equity curve of the portfolio
        #TODO: Currently only handles signals for one ticker - need to modify to handle more
        :return:
        """
        # Plot the equity curve in dollars
        events, event_dates, trade_count = self.generate_events(self, start_date, end_date)
        ax = self.setup_figure(self, trade_count)
        data = self.get_data(self)
        self.plot_data(self, ax, data)
        self.create_table(self, events, event_dates)

        return trade_count

        #fig.show()






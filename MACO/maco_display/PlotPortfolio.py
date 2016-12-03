#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 11/05/2016

"""
import matplotlib.pyplot as plt
import numpy as np

from MACO.maco_display.Plotter import Plotter
from MACO.maco_display.Table import Table


class PlotPortfolio(Plotter, Table):

    def __init__(self, portfolio, returns, events, event_dates, trades):
        self.portfolio = portfolio
        self.securities = portfolio.market_on_close_securities
        self.returns = returns
        self.tickers = [t.symbol for t in self.securities]
        self.events = events
        self.event_dates = event_dates
        self.trades = trades

    def setup_figure(self, event_count=None):
        """
        Creates and formats figure that contains a time-series graph and table
        """
        # Figure starts at a height of 4 inches and increments an inch every 4 events
        # Used for styling
        size = (self.trades / 4) + 4

        fig = plt.figure(figsize=(15, size))
        fig.patch.set_facecolor('silver')
        fig.suptitle('Portfolio snapshots', fontsize=14, fontweight='bold')
        ax = fig.add_subplot(211)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time')
        ax.set_ylabel('Portfolio value in $ (USD)')

        return ax

    def get_data(self):
        """
        Determine the x and y coordinates for signals to buy or sell stock.
        The x-axis are Dates, and Y-axis is the value of the moving averages
        """
        portfolio_data = []
        for security in self.securities:
            # All buy signal dates for the portfolio (X-cord)
            security_data = [self.returns.ix[security.signals.positions == 1.0].index]
            # The value of the portfolio for each buy signal (Y-cord)
            security_data.append(self.returns.total[security.signals.positions == 1.0])
            # All sell signal dates for the portfolio (X-cord)
            security_data.append(self.returns.ix[security.signals.positions == -1.0].index)
            # The value of the portfolio for each sell signal (Y-cord)
            security_data.append(self.returns.total[security.signals.positions == -1.0])
            portfolio_data.append(security_data)

        return portfolio_data

    def plot_data(self, ax, data):
        # Plot portfolio returns
        ax.plot(self.returns['total'], color='navy', lw=3)

        # Colors are determined by the Set3 spectrum, evenly spaced for each security
        colors = plt.cm.Set3(np.linspace(0, 1, len(self.securities)))

        # Identify each trade made for the portfolio and place a market on the portfolio return curve
        for i, security in enumerate(self.securities):
            ax.plot(data[i][0], data[i][1], '^', markersize=9, color=colors[i], label=str(security.symbol))
            ax.plot(data[i][2], data[i][3], 'v', markersize=9, color=colors[i], label='_nolegend_')

        plt.legend(numpoints=1, prop={'size': 7})

    def create_cell_text(self, b_dates=None, s_dates=None):
        table = []
        # Create a table row for each event
        table_data = self.returns.copy(deep=True)
        # Remove database keys and price_date from the dataframe
        table_data.drop(['id', 'maco_id', 'price_date', 'created_date'], axis=1, inplace=True)
        for d in self.event_dates:
            event_list = self.events[d.strftime("%Y-%m-%d")]
            # Some dates have multiple events
            for e in event_list:
                row = [d.strftime("%Y-%m-%d")]
                row.append(e)
                try:
                    row.extend(table_data.ix[d].values[:-1])
                except Exception as e:
                    print "E: " + str(e)

                table.append(row)

        return sorted(table)

    def create_row_labels(self, num_of_rows):
        rows = []
        for i in range(num_of_rows):
            rows.append(i + 1)
        return rows

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

    def create_table(self, data=None):
        cell_text = self.create_cell_text()
        row_labels = self.create_row_labels(len(cell_text))

        column_labels = ['Date', 'Event', 'Holdings', 'Cash', 'Total']
        column_labels[2:2] = self.tickers

        colors = self.create_table_colors(row_labels, len(column_labels), cell_text)

        table = plt.table(cellText=cell_text, cellColours=colors[0],
                          rowColours=colors[1], rowLabels=row_labels,
                          colColours=colors[2], colLabels=column_labels,
                          bbox=[0.0, 0.0, 1.0, 1.0],
                          cellLoc='bottom')

        plt.tight_layout()
        table.set_fontsize(9)

    def plot_equity_curve(self):
        """
        Plot the equity curve of the portfolio in dollars and display trade table showing
        the state of the portfolio at event-specific time frames.
        """
        # Plot the equity curve in dollars and display trade table
        ax = self.setup_figure()
        data = self.get_data()
        self.plot_data(ax, data)
        self.create_table()

    def setup_graph(self):
        fig = plt.figure(figsize=(12, 5))
        fig.patch.set_facecolor('silver')
        fig.suptitle('Backtested Portfolio Results', fontsize=14, fontweight='bold')
        ax = fig.add_subplot(111)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time Horizon of Backtest')
        ax.set_ylabel('Portfolio value in $ (USD)')
        return ax

    def plot_large_equity_curve(self):
        """
        Same as plot_equity_curve but for larger portfolios will split the equity curve and
        trade table into two different figures for readability
        """
        ax = self.setup_graph()
        data = self.get_data()
        self.plot_data(ax, data)

        # Second figure is a table showing holdings and total value of portfolio as different events occur
        size = (self.trades / 4) + 4
        fig = plt.figure(figsize=(12, size))
        # Styling to remove axis from overlapping table
        plt.axis('off')
        self.create_table()






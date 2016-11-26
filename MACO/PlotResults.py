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
import matplotlib.dates as md

class PlotResults(Plotter):

    def __init__(self, results):
        self.results = results

    @staticmethod
    def setup_figure(self):
        """
        Creates and formats time-series graph
        :param number_of_events: Int - Used for determining height of the figure
        :return: The figure
        """
        # Figure starts at a height of 4 inches and increments an inch every 4 events
        #size = (event_count / 4) + 4
        fig = plt.figure(figsize=(15, 5))
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

        #(Start, price) #(End, price)
        print "self.results"
        print self.results
        points = []
        for index, row in self.results.iterrows():
            start_point = row['start_date'], row['start_capital']
            end_point = row['end_date'], row['end_capital']
            points.append([start_point, end_point])

        return points

    @staticmethod
    def plot_data(self, ax, data):
        #colors = plt.cm.plasma(np.linspace(0, 1, len(self.securities)))

        for p in data:
            print "p is: "
            print p[0][0]
            print p[0][1]

            fig = plt.figure()
            ax = fig.add_subplot(111)
            t0 = datetime.datetime(1998, 1, 2)
            t = [t0 + datetime.timedelta(days=j) for j in xrange(6570)]
            y = [1000000] * 6570
            ax.plot(t, y)


            #ax.plot(data[i][0], data[i][1], '^', markersize=10, color=colors[i], label=str(security.symbol))
            x1 = md.date2num(p[0][0])
            x2 = md.date2num(p[1][0]) - x1

            #x0 = md.date2num(datetime.datetime(2015, 4, 5))

            #xw = md.date2num(datetime.datetime(2015, 4, 7)) - x0
            #ax.arrow(x1, p[0][1], x2, p[1][1], head_width=0.05, head_length=0.1, fc='k', ec='k')
            arr = plt.Arrow(x1, p[0][1], x2, p[1][1], edgecolor='black')
            ax.add_patch(arr)
            arr.set_facecolor('b')
            fig.autofmt_xdate()
            plt.show()

        plt.legend(numpoints=1)


    def plot_graph(self):
        """
        Plot the equity curve of the portfolio
        #TODO: Currently only handles signals for one ticker - need to modify to handle more
        :return:
        """

        ax = self.setup_figure(self,)
        data = self.get_data(self)
        self.plot_data(self, ax, data)

        #self.create_table(self, events, event_dates)

        return trade_count

        #fig.show()






#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 12/04/2016

"""
import matplotlib.pyplot as plt

from MACO.maco_display.Plotter import Plotter


class PlotVolumeAnalysis(Plotter):
    def __init__(self, small_backtest, large_backtest):
        self.s_backtest = small_backtest
        self.l_backtest = large_backtest

    def setup_figure(self, event_count=None):
        """
        Creates and formats time-series graph comparing low and high volume portfolios
        """
        fig = plt.figure(figsize=(10, 5))
        fig.patch.set_facecolor('silver')
        fig.suptitle(
            'Entire Universe - Equity Curve Comparison',
            fontsize=14, fontweight='bold')
        ax = fig.add_subplot(111)
        ax.set_axis_bgcolor('beige')
        ax.set_xlabel('Time')
        ax.set_ylabel('Portfolio value in $ (USD)')
        return ax

    def get_data(self):
        s_total = []
        l_total = []
        for s in self.s_backtest:
            s_total.append(s['total'])

        for l in self.l_backtest:
            l_total.append(l['total'])

        return s_total, l_total

    def plot_data(self, ax, data, return_type):
        if return_type == 'small':
            for security in data:
                #ax.plot(security, 'darkred', lw=1)
                ax.plot(security, 'navy', lw=1)

        else:
            for security in data:
                #ax.plot(security, 'tomato', lw=1)
                ax.plot(security, 'c', lw=1)

    def plot_results(self):
        """
        Plot both low-volume and high-volume portfolios for comparison. Also include
        portfolio table to identify some key parameters, indicators, and results for each portfolio.
        """
        ax = self.setup_figure()
        portfolio_returns = self.get_data()

        print "portfolio_returns is: "
        print portfolio_returns

        # Plot small-volume results
        self.plot_data(ax, portfolio_returns[0], 'small')

        # Plot large-volume results
        self.plot_data(ax, portfolio_returns[1], 'large')
        ax.legend(['Small Volume Portfolio', 'Large Volume Portfolio'], loc=2)
        ax.axhline(y=100000, linewidth=2, color='k')
        leg = ax.get_legend()
        #leg.legendHandles[0].set_color('darkred')
        #leg.legendHandles[1].set_color('tomato')
        leg.legendHandles[0].set_color('navy')
        leg.legendHandles[1].set_color('c')
        for legobj in leg.legendHandles:
            legobj.set_linewidth(2.0)





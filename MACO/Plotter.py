#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Justin Dano 11/11/2016


from abc import ABCMeta, abstractmethod


class Plotter(object):
    """
    Abstract Base class for a Plotting graphs with Matplotlib
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def setup_figure(self, count):
        """Initial setup for graphics, such as size, color, subplots, ect."""
        raise NotImplementedError("Must implement setup_figure()!")

    @abstractmethod
    def get_data(self):
        """Generates the data used in graphs, typically from a Portfolio object"""
        raise NotImplementedError("Must implement get_data()!")

    @abstractmethod
    def plot_data(self, ax, data):
        """Plots the data on the graph"""
        raise NotImplementedError("Must implement get_data()!")


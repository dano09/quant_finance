#!/usr/bin/python
# -*- coding: utf-8 -*-

# Author: Justin Dano 10/23/2016
# Design inspired by articles on Quantstart.com

from abc import ABCMeta, abstractmethod


class Strategy(object):
    """
    Abstract Base class for trading strategies. The Goal of the class is to
    output list of signals in the form of a time series pandas DataFrame.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_signals(self):
        """Provides logic to create a Dataframe containing signals:
        1 (Long), 0 (Hold), and -1 (Short) based on the strategy."""
        raise NotImplementedError("Must implement generate_signals()!")

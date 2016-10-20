#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Justin Dano 10/1/2016

For my local machine, I use this script to handle my cron jobs and is always running. As of this writing we have
scripts running either once a month, or every day depending on their function.
"""

from subprocess import call
from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
import time


def monthly_scripts():
    """
    Handles monthly maintenance scripts. Currently all we run on a monthly basis is adding any new companies from the
    S&P500 to our universe, and delisting any tickers that no longer trade publicly.
    """
    start_time = time.time()
    print "Get any new tickers for our database"
    call(['python', 'ObtainSymbols.py'])
    print "\n Finished ObtainSymbols script \n"
    sleep(5)

    print "Now lets remove any delisted tickers"
    call(['python', 'DelistStocks.py'])
    print "\n Finished DelistStocks script \n"

    print("---Monthly maintenance scripts took %s seconds ---" % (time.time() - start_time))


def daily_scripts():
    """
    Handles the running of daily scripts. First, it collects data from both vendors, cross-references the data, and
    finally interpolates any missing values due to inconsistencies between the vendors.
    :return:
    """
    start_time = time.time()
    print "Collecting Data from Yahoo"
    call(['python', 'ObtainYahooPriceData.py'])
    print "\n Finished with Yahoo \n"
    sleep(5)

    print "\n Collecting Data from Quandl"
    call(['python', 'ObtainQuandlPriceData.py'])
    print "\n Finished with Quandl \n"
    sleep(5)

    print "\n Now clean data from Yahoo and Quandl \n"
    call(['python', 'CleanPricingData.py'])
    print "\n Finished comparing data \n"
    sleep(5)

    print "\n Now lets fill any missing data \n"
    call(['python', 'FillZeros.py'])
    print "\n Finished cleaning data \n"

    print("---Today's work took %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
    scheduler = BackgroundScheduler()

    scheduler.add_job(monthly_scripts, 'cron', day=1, hour=20, minute=1)
    scheduler.add_job(daily_scripts, 'cron', hour=21, minute=1)

    scheduler.start()
    while True:
        sleep(1)

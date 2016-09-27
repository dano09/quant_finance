# Quantitative Backtesting

This project details the creation of a backtesting engine that will be used in analysis of financial securities and also to backtest algorithmic trading strategies. The majority of the setup is completed with open source software, a MySQL database and the Python scripting language. Some additional frameworks include Pandas, and Numpys.

Most of the scripts provided have the functionality to run daily as chron tasks, or used over a lookback period to gather and clean historical data. If a script has this functionality, please review the main method for adjusting the date parameters.

For example, I would adjust the parameters to get price data for the companies in the S&P500 from January 1st, 1998 up to September 26th, 2016. I would then set the scripts up to just run over a single date, and create a cron task to have it run everyday.

The first section of this project is retrieving and cleaning data. A of this writing, the work flow is as follows:

PART 1: Get historical data (1998-2016)
1. Create needed database tables
2. Run obtainSymbols.py [Collect tickers of companies we wish to analyze]
3. Run obtainYahooPriceData
4. Run obtainQuandlPriceData
5. Run cleanPricingData
6. Run fillZeros

This will generally take awhile. For example obtainYahooPriceData took about 10 minutes (it collects over 2 million data points). This process is only to be done once though, and did not deem worthy of a performance overhaul.

PART 2: Collecting daily data 
Next adjust the date parameters for any scripts that are required and set cron tasks for the following scripts.
1. obtainSymbols.py (Runs once a month)
2. Run obtainYahooPriceData (Everyday at 9:00PM)
3. Run obtainQuandlPriceData (Everyday at 9:05PM)
4. Run cleanPricingData (Everyday at 9:15PM)
5. Run fillZeros (Everyday at 9:30)

Collecting data from Yahoo and Quandl can go in any order, but cleaningPriceData.py can only work after data has been collected from both vendors. Finally, fillZeros.py is made to run after cleanPricingData.py

I have started a blog (jdano.com) that will provide more documentation on each script and the algorithms that were implemented. This blog should be live sometime by the end of October, 2016.

DISCLAIMER: Everything written here is the IP of Justin Dano, and is in no way involved with his employer. This project has coalesced from what Justin has learned from self-study. While the work here details how one could make trading algorithms, it is not intended to be used with real money.

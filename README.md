# Quantitative Backtesting

ABSTRACTION:

This project details the creation of a Securities database that will be used in analysis of financial securities and also to backtest algorithmic trading strategies. The majority of the setup is completed with open source software, a MySQL database and the Python scripting language. Credit also goes to the Micheal Halls-Moore, for his articles on Quantstart.com helped me in the creation of some of the work.

INTRODUCTION:

1 - To start, I have created 3 tables in a MySQL Database which is stored on my local computer for the time being. As you can see below, I have created 3 tables, Vendor, Daily_Price, and Symbol.

![Alt text](https://github.com/dano09/quant_finance/blob/master/images/database_schema.PNG "Schema")

2 - Running obtainSymbols.py will scrape the ticker symbols for each company from the S&P500 index and save the ticker symbols to my databases Symbol table. I run this script once a month through Task Scheduler (I use Windows 10) to make sure I collect price data for the largest companies. I have included a screenshot of a small section of the Symbol table below.

![Alt text](https://github.com/dano09/quant_finance/blob/master/images/symbolTable.PNG "Schema")

NOTE: Once a company's symbol is added to the database, I will continue to collect its pricing data even if it's removed from the S&P500 list. I have no intent on modeling just the SP500 but rather used the index as an approximation to the market. This helps prevent survivorship bias in our backtesting, which can result in inflated returns for trading strategies. For our purposes the more data points we have, the better.

3 - Finally we will run the obtainPriceData.py to actually collect the pricing data. The pricing data we are interested in is the daily Open, Low, Close, High, Adjusted_Close_Price and Volume (OLCHAV) data. The script will iterate through the ticker symbols, and connect to Yahoo Finance for the CSV data. The script proceeds to add the data to the Daily_Price table of our database. Below is a snapshot of some of Googles recent OLCHAV data.


![Alt text](https://github.com/dano09/quant_finance/blob/master/images/price_data_from_google.PNG "Schema")

This script is ran everyday through windows Task scheduler. Logic is in place to avoid adding null data points for weekends and holidays. If for some reason the connection to Yahoo's servers fail, the ticker for that company will be saved in a file that is stored on my local C Drive. My backlog has a maintenance script to handle missing data values, since the accuracy of pricing data is pertinent to creating accurate models. Much more on data wrangling to come.

CONCLUSION: So far we have a general process for collecting pricing data for hundreds of companies. We are well on our way to having the infrastructure in place for analyzing securities. Pricing data is far from simple however, and it is imperative we verify the correctness of the data to avoid errors and also to minimize biases. Future work will involve cleaning the data and accounting for potential problems such as how to incorporate M/A, pricing errors from vendors, missing data, and incorrect data.

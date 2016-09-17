import pandas as pd
import MySQLdb as mdb

def get_db_connection():
	db_host = 'localhost'
	db_user = 'root'
	db_pass = 'GoldfishSmiles.com'
	db_name = 'Securities_master3'
	return mdb.connect(db_host, db_user, db_pass, db_name)

def retrieve_db_tickers(connection):
    """
    Retrieve ticker symbols for each company from
    the database.
    :param connection:
    :return: List of all tickers from database
    """
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT id, ticker FROM symbol")
        data = cur.fetchall()
        return [(d[0], d[1]) for d in data]


def retrieve_price_data(con, ticker, vendor_id, start, end):
	"""
	Retrive price data from the database for the specific
	ticker over the specified range.
	:param ticker: The company's ticker symbol
	:param vendor_id: The vendor we grab the price data from
	:param start: We grab data starting at this date
	:param end: The data ends at this date
	:return:Dataframe of all the price data
	"""
	with con:
		cur = con.cursor()
		# First query is to retrieve the id for the given symbol
		cur.execute("SELECT id FROM symbol WHERE ticker = %s", [ticker])
		ticker_id = cur.fetchall()
		ticker_id = ticker_id[0][0]
		# Second query gathers OHLCAV data
		cur.execute("SELECT * FROM daily_price WHERE \
		symbol_id = %s AND data_vendor_id = %s \
		AND price_date BETWEEN %s AND %s", (ticker_id, vendor_id, start, end))

		# Return none if no data exists for the ticker within the specified
		# time frame, otherwise return a dataframe with the OHLCAV data
		if not cur.rowcount:
			if vendor_id == 1:
				print "Yahoo had no price data available for " + str(start)
			else:
				print "Quandl had no price data available for " + str(start)
			price_data = None
		else:
			price_data = pd.DataFrame(list(cur.fetchall()))
			price_data.columns = ['id', 'symbol_id', 'vendor_id', 'price_date', 'created_date',
			                      'last_updated_date', 'open_price', 'high_price', 'low_price', 'close_price',
			                      'adj_close_price', 'volume']

		return price_data

def retrieve_data_with_zeros(con, ticker, start, end):
	"""

	:param con:
	:param ticker:
	:param start:
	:param end:
	:return:
	"""
	with con:
		cur = con.cursor()
		# First query is to retrieve the id for the given symbol
		cur.execute("SELECT id FROM symbol WHERE ticker = %s", [ticker])
		ticker_id = cur.fetchall()
		ticker_id = ticker_id[0][0]
		# Second query gathers OHLCAV data
		#cur.execute("SELECT * FROM clean_prices WHERE \
		#symbol_id = %s AND price_date BETWEEN %s AND %s", (ticker_id, start, end))
		cur.execute("SELECT * FROM clean_prices2 WHERE \
		symbol_id = %s AND price_date >= %s AND price_date <= %s", (ticker_id, start, end))
		# Return none if no data exists for the ticker within the specified
		# time frame, otherwise return a dataframe with the OHLCAV data
		if not cur.rowcount:
			print "No price data available for " + ticker + " on " + str(start)
			price_data = None
		else:
			price_data = pd.DataFrame(list(cur.fetchall()))
			price_data.columns = ['id', 'symbol_id', 'price_date', 'created_date',
			                      'last_updated_date', 'open_price', 'high_price', 'low_price', 'close_price',
			                      'adj_close_price', 'volume']

		return price_data

def insert_data_into_db(con, price_data):
	"""
	Insert Dataframe into SQL database
	:param price_data: OHLCAV data
	"""
	#print "about to insert into price_data into db:"
	#print price_data
	#price_data['symbol_id'] = ticker
	#print "new price_data"
	#print price_data
	#sys.exit()
	with con:
		price_data.to_sql(con=con, name='clean_prices3', if_exists='append', index=False, flavor='mysql')

def delete_duplicates(con, table, symbol_id, price_date):
	"""

	:param con:
	:param table:
	:param symbol_id:
	:param price_date:
	:return:
	"""

	with con:
		cur = con.cursor()
		# First query is to retrieve the id for the given symbol
		cur.execute("SELECT id FROM symbol WHERE ticker = %s", [ticker])
		cur.execute("DELETE %s FROM %s INNER JOIN (select")

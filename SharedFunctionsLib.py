
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
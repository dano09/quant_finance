def retrieve_db_tickers(connection):
    with connection:
        cur = connection.cursor()
        cur.execute("SELECT id, ticker FROM symbol")
        data = cur.fetchall()
        return [(d[0], d[1]) for d in data]
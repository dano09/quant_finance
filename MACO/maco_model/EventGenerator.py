from datetime import datetime

import pandas as pd


class EventGenerator:

    def __init__(self, portfolio, backtest_results):
        self.portfolio = portfolio
        self.securities = portfolio.market_on_close_securities
        self.backtest_results = backtest_results

    def get_data(self):
        portfolio_data = []
        for security in self.securities:
            # Buy signal dates
            security_data = [self.backtest_results.ix[security.signals.positions == 1.0].index]
            # Buy signal prices
            security_data.append(self.backtest_results.total[security.signals.positions == 1.0])
            # Sell signal dates
            security_data.append(self.backtest_results.ix[security.signals.positions == -1.0].index)
            # Sell signal prices
            security_data.append(self.backtest_results.total[security.signals.positions == -1.0])
            portfolio_data.append(security_data)

        return portfolio_data

    def create_event(self, date, signal, symbol, bars):
        price = bars.loc[date]['close_price']
        if signal is 'b':
            event = "B:" + symbol + " @ " + "%.2f" % price
        else:
            event = "S:" + symbol + " @ " + "%.2f" % price

        return event

    def add_event(self, date, event, events):
        # Create a new event
        if date not in events:
            events[date] = [event]

        # An event already exists for this date, so we add an additional one
        else:
            event_list = events.get(date)
            event_list.append(event)
            events[date] = event_list

    def generate_events(self, start_date, end_date):
        events = {start_date: ["Start Date"], end_date: ["End Date"]}
        # Converting strings to datetime
        event_dates = [datetime.strptime(start_date, '%Y-%m-%d').date(),
                       datetime.strptime(end_date, '%Y-%m-%d').date()]

        data = self.get_data()

        # FOR EACH SECURITY
        for i, security in enumerate(self.securities):

            # Create event string for each buy signal
            for date in data[i][0].values:
                if date not in event_dates:
                    event_dates.append(date)

                event = self.create_event(date, 'b', security.symbol, security.bars)
                self.add_event(date.strftime("%Y-%m-%d"), event, events)

            # Create event string for each sell signal
            for date in data[i][2].values:
                if date not in event_dates:
                    event_dates.append(date)

                event = self.create_event(date, 's', security.symbol, security.bars)
                self.add_event(date.strftime("%Y-%m-%d"), event, events)

        return events, event_dates

    def get_trade_count(self):
        # Add up total number of trades for given backtest
        count_total = 0
        for security in self.securities:
            counts = security.signals['positions'].value_counts()
            count_total += counts.loc[1.0]
            count_total += counts.loc[-1.0]

        return count_total


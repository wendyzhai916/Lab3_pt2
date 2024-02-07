import yfinance as yf
from datetime import datetime, timedelta

def forecast_price(purchase_date, ticker):
    return latest_data


def current_price(ticker, date):
    forecast_result = forecast_price(datetime.today().strftime("%Y-%m-%d"), ticker)
    date_price_dict = forecast_result.set_index('Date')['open'].to_dict()
    date_price_dict = {str(key.date()) : value for key,value in date_price_dict.items()}
    current_price = date_price_dict[date]
    return current_price


class Portfolio:
    def _init_(self, name, initial_asset):
        self.name = name
        self.initial_asset = initial_asset
        self.total_investment = initial_asset
        self.stocks = {}
        self.stock_holdings = {}

        ticker_input = input("Please enter the stock tickers interested in (split by \','\, eg. AAPL,MSFT): ")
        tickers = [ticker.strip().upper() for ticker in ticker_input.split(',')]

        for ticker in tickers:
            try:
                stock_data = yf.Ticker(ticker)
                todays_data = stock_data.history(period='id')
                opening_price = todays_data['Open'].iloc[0]
                self.stocks[ticker] = opening_price
                print(f"The opening price for {ticker} today is: ${opening_price:.2f}")
            except Exception as e:
                print(f"Error fetching {ticker}. Error: {e}")

        print(self.stocks)
        print(f"Portfolio {self.name} created successfully")


    def forecast_all_stocks(self, ticker = None):
        forecast_results = []
        print("Forecasting the open price for the next 7 days...")
        print('\n')
        # calculate the range of dates for the next 7 days
        start_date = datetime.today()
        end_date = start_date + timedelta(days=7)

        tickers_to_forecast = [ticker] if ticker else self.stocks.keys()

        for t in tickers_to_forecast:
            forecast_list = []
            forecast = forecast_price(datetime.today().strftime("%Y-%m-%d"), t)
            # filter data within 7 days
            forecast = forecast[(forecast['Date'] > start_date) & (forecast['Date'] <= end_date)]
            # convert  data index to string format for better representation
            forecast['Date'] = forecast['Date'].dt.strftime('%Y-%m-%d')
            forecast_dict = forecast.set_index('Date')['Open'].to_dict()
            for date, value in forecast_dict.items():
                forecast_list.append({date: value})
            forecast_results.append({
                'Ticker': t,
                'Forecast': forecast_list
            })

        return forecast_results
    

    def buy_stock(self):
        ticker = input("Please enter the stock you wish to buy(just input one stock ticker): ").upper()
        if ticker not in self.stocks:
            print(f"Please include {ticker} in the interest list first")

        # Get the forecast price for the next 7 days
        forecast_prices = {}
        for forecast in self.forecast_all_stocks(ticker):
            if forecast['Ticker'] == ticker:
                for daily_forecast in forecast['Forecast']:
                    forecast_prices.update(daily_forecast)
                break
        if not forecast_prices:
            print("Unable to fetch the forecasted price for the chosen stock")
        
        # print out the forecast price
        print(f"The forecasted stock prices for {ticker} in the next 7 days are: ")
        for date, price in forecast_prices.items():
            print(f"{date}: ${price:.2f}")
        
        # select a date and share number to purchase
        purchase_date = input(f"Enter the date (from the above) that you wish to buy the stock {ticker}(YYYY-MM-DD): ")
        if purchase_date not in forecast_prices:
            print("The date you entered is invalid")
        try:
            quantity = int(input(f"Please input the shares number of {ticker} you wish to buy: "))
            purchase_price = forecast_prices[purchase_date] * quantity
            if purchase_price > self.total_investment:
                print(f"You don't have enough money remained to buy {quantity} shares of {ticker}")
            # update Portfolio variable
            self.total_investment = self.total_investment - purchase_price
            if ticker in self.stock_holdings:
                self.stock_holdings[ticker] += quantity
            else:
                self.stock_holdings[ticker] = quantity
            print(f"Successfully purchased {quantity} shares of {ticker} on {purchase_date}, using dollars: ${purchase_price:.2f}")
            print(f"The remaining investment assets after this purchase: {self.total_investment}")
            # update the stock's price for the next day using the forecasted price of the chosen date
            next_day = (datetime.strptime(purchase_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            if next_day in forecast_prices:
                self.stocks[ticker] = forecast_prices[next_day]
            else:
                print(f"No forecasted price available for {next_day}. Keeping the last know price for {ticker}")
            # recalculate current portfolio value
            portfolio_value = self.total_investment
            for stock, amount in self.stock_holdings.items():
                portfolio_value = portfolio_value + amount * self.stocks[stock]
            print(f"The current portfolio value is ${portfolio_value:.2f}")
            
        except Exception as e:
            print(f"Error occurs. Error: {e}")
    

    def sell_stock(self):
        ticker = input("Please enter the stock ticker you wish to sell(just input one stock): ").upper()
        if ticker not in self.stocks:
            print(f"Sorry, you do not have {ticker} in your assets")
            return
        
        # get the forecasted prices for the ticker
        forecast_prices = {}
        for forecast in self.forecast_all_stocks(ticker):
            if forecast['Ticker'] == ticker:
                for daily_forecast in forecast['Forecast']:
                    forecast_prices.update(daily_forecast)
                break
        print(f"The forecasted stock prices for {ticker} in the next 7 days are: ")
        for date, price in forecast_prices.items():
            print(f"{date}: ${price:.2f}")

        # let user input date and shares they want to sell
        sell_date = input(f"Enter the date (from the above) that you wish to sell the stock {ticker}(YYYY-MM-DD): ")
        if sell_date not in forecast_prices:
            print("The date you entered is invalid")
            return
        quantity = int(input(f"Please input the shares number of {ticker} you wish to sell: "))
        if quantity > self.stock_holdings.get(ticker, 0):
            print(f"Sorry, you do not have enough shares of {ticker} in the assets")
            return
        
        # update portfolio variable
        sell_price = forecast_prices[sell_date]
        transaction_value = sell_price * quantity
        self.total_investment = self.total_investment + transaction_value
        self.stock_holdings[ticker] -= quantity
        if self.stock_holdings[ticker] <= 0:
            del self.stock_holdings[ticker]
        print(f"Successfully sold {quantity} shares of {ticker} on {sell_date}, using dollars: ${transaction_value:.2f}")
        print(f"The total investment assets after this selling: {self.total_investment}")

        # adjust the price for the next day
        previous_day = (datetime.strptime(sell_date, "%Y-%m-%d")).strftime("%Y-%m-%d")
        if previous_day in forecast_prices:
            self.stocks[ticker] = forecast_prices[previous_day]
        # current portfolio value
        portfolio_value = self.total_investment
        for stock, amount in self.stock_holdings.items():
            portfolio_value = portfolio_value + amount * self.stocks(stock, 0)

        print(f"The current portfolio value is ${portfolio_value:.2f}")

    
    def get_portfolio_value(self, date):
        start_date = datetime.today()
        end_date = start_date + timedelta(days=7)
        # convert string to datetime
        input_date = datetime.strptime(date, "%Y-%m-%d")
        if input_date < start_date or input_date > end_date:
            print(f"Error. The date you provided is out of prediction range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} ")
            return
        stock_value = 0
        # calculate the value of each stock based on the input date
        for ticker, quantity in self.stock_holdings.items():
            stock_price = current_price(ticker, date)
            stock_value += quantity * stock_price
            print(f"Stock Name: {ticker}, Share Amount: {quantity}, Total Accumulative Values: {stock_price:.2f}")
        # compute total value of stoks in the portfolio
        total_asset = self.total_investment + stock_value
        # calculate overall profit
        profit = total_asset - self.initial_asset

        print(f"The total profit of Portfolio {self.name} is: {profit:.2f}")
        print(f"Profit = total_asset - initial_asset = ({self.total_investment:.2f} + {stock_value:.2f}) - {self.initial_asset}")
        return 
    

if __name__ == '__main__':

    while True:
        print('-------------------Stock Trading System----------------')
        print('Options Including:')
        print('1. Create your portfolio')
        print('2. Buy stock')
        print('3. Sell stock')
        print('4. Display profits of the portfolio')
        print('5. Show evaluation metrics ')
        print('6. Exit the system')
        print('\n')
        print('-------------------LET\'S GET STARTED-------------------')

        choice = input("Please enter your choice of the options: ")

        if choice == "1":
            initial_investment = float(input("Please type in your initial investment amout： "))
            port_name = input("Please type in your portfolio name： ")
            portfolio = Portfolio(port_name, initial_investment)

        elif choice == "2":
            portfolio.buy_stock()

        elif choice == "3":
            portfolio.sell_stock()

        elif choice == "4":
            date = input(f"Please input a date that you wish to see the total profit of {port_name}")
            portfolio.get_portfolio_value(date)

        elif choice == "5":
            pass

        elif choice == "6":
            print("Exiting...")
            break

        else:
            print("Invalid choice, please try a valid option")


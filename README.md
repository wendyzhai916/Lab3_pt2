## Lab3_pt2

### Overview

This Python program implements a simple stock trading system that allows users to create a portfolio, buy and sell stocks, and display the profits of their portfolio. It utilizes the Yahoo Finance API (`yfinance`) to fetch real-time stock data and performs forecasting of stock prices for the next 7 days using a simple LSTM model.

### Requirements

- Python 3.x
- `requirements.txt` packages
- mysql

### Usage

1. **Running the Program:**

Attain access to the server via the following command

```bash
sudo mysql -u root -p
```

Download the necessary packages

```bash
python3 -m pip install -r requirements.txt
```

Run the script `stock_trading_system.py` using a Python interpreter.

```bash
python stock_trading_system.py
```


2. **Options:**

Upon running the program, users are presented with a menu of options:

- **Create your portfolio:** Allows users to create a portfolio by specifying an initial investment amount and a name for the portfolio. Users can also input a list of stock tickers they are interested in.
   
- **Buy stock:** Enables users to buy stocks from their portfolio. Users can specify the stock they wish to buy, the number of shares, and the date of purchase.

- **Sell stock:** Facilitates selling stocks from the portfolio. Users can specify the stock they wish to sell, the number of shares, and the date of sale.

- **Display profits of the portfolio:** Allows users to view the total profit of their portfolio on a specific date.

- **Show evaluation metrics:** Placeholder option for future functionality.

- **Exit the system:** Terminates the program.

3. **Note:**

- The program fetches real-time stock data and performs forecasting using an LSTM model as well as a moving aveerage model. It allows users to simulate buying and selling stocks based on the forecasted prices.
- Users can interact with the system to manage their portfolio and track profits over time.

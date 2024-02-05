import os
import mysql.connector
import pandas as pd
import numpy as np
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('MYSQL_HOST')
USER = os.getenv('MYSQL_USER')
PASSWORD = os.getenv('MYSQL_PASSWORD')
DATABASE = os.getenv('MYSQL_DATABASE')

def connect_to_database(host, user, password, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        print("Connected to MySQL database")
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute(""" CREATE TABLE IF NOT EXISTS Portfolio (portfolio_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR)""")
    cursor.execute(""" CREATE TABLE IF NOT EXISTS Stock ( stock_id INT AUTO_INCREMENT PRIMARY KEY,
                    portfolio_id INT, symbol VARCHAR(10), date DATE, open DECIMAL(10, 2),
                    high DECIMAL(10, 2), low DECIMAL(10, 2), close DECIMAL(10, 2), adj_close DECIMAL(10, 2),
                    volume INT, daily_returns DECIMAL(10, 2), pct_change DECIMAL(10, 2),
                    FOREIGN KEY (portfolio_id) REFERENCES Portfolio(portfolio_id) """)
    conn.commit()
    print("Tables created successfully")

def fetch_stock_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    data_fill = data[['Open','High','Low','Close','Adj Close']]
    data_fill = data_fill.interpolate(method='time')
    data_fill['Volume'] = data['Volume'].interpolate()
    data_fill['Daily Returns'] = data_fill['Close'] - data_fill['Open']
    data_fill['Percent Change'] = round(data_fill['Daily Returns']/data_fill['Open']*100,2)

    return data_fill

def populate_stock_table(conn, portfolio_id, stocks, start_date, end_date):
    cursor = conn.cursor()
    for stock in stocks:
            data = fetch_stock_data(stock, start_date, end_date)
            for index, row in data.iterrows():
                    cursor.execute("""
                                    INSERT INTO Stock (portfolio_id, symbol, date, open, high,
                                    low, close, adj_close, volume, daily_returns, pct_change)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (portfolio_id, stock, index, row['Open'], row['High'], row['Low'],\
                                    row['Close'], row['Adj Close'], row['Volume'], row['Daily Returns'],\
                                    row['Percent Change']))
    conn.commit()
    print("Stock data inserted successfully")


def main():
    host = HOST
    user = USER
    password = PASSWORD
    database = DATABASE
    conn = connect_to_database(host, user, password, database)
    create_tables(conn)

    portfolio_id = 1
    stocks = ['AAPL', 'MSFT', 'GOOG']
    start_date = '2024-01-01'
    end_date = '2024-01-31'
    populate_stock_table(conn, portfolio_id, stocks, start_date, end_date)

    conn.close()
    print("Database connection closed")

if __name__ == "__main__":
    main()
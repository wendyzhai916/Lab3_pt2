import mysql.connector
import yfinance as yf
from prettytable import PrettyTable
from sqlalchemy import create_engine
import pandas as pd
import os


# display the portfolio using the prettytable package
def data_show(show):
    if show == 'n':
        return
    cursor = connection.cursor()
    select_query = f'SELECT * FROM {name}'
    cursor.execute(select_query)
    column_names = [desc[0] for desc in cursor.description]
    result_set = cursor.fetchall()
    table = PrettyTable(column_names)
    for row in result_set:
        table.add_row(row)
    print(table)
    cursor.close()


if __name__ == '__main__':

    print('-------------------CREATING PORTFOLIOS------------------')
    print('Steps Including:')
    print('1.Create portfolio with input name')
    print('2.Define stocks and date to be included in the portfolio')
    print('3.Display portfolio')
    print('\n')
    print('-------------------LET\'S GET STARTED-------------------')
    # connect to database
    db_config = {
        'host' : 'localhost',
        'user' : 'root',
        'password' : 'DSCI560',
        'database' :'yfinance',
    }
    connection = mysql.connector.connect(**db_config)

    try:
        # Establish portfolio 
        name = input('Please enter your portfolio name: ')
        stocks = input('Please enter the list of stocks to be included(split by \',\'): ')
        dates = input('Please enter the start and end date to be included(YYYY-MM-DD,split by \',\'): ')
        print('Creating Portfolio \'{}\': '.format(name))
        print('\n')
        stock_list = stocks.split(',')
        start_date = dates.split(',')[0]
        end_date = dates.split(',')[1]
        stock_invalid = []
        stock_valid = []

        try:
            engine = create_engine('mysql+mysqlconnector://root:DSCI560@localhost/yfinance'.format(**db_config))
            stocks_data = pd.DataFrame()
            for symbol in stock_list:
                stock = yf.download(symbol, start=start_date, end=end_date)
                if stock.empty:
                    stock_invalid.append(symbol)
                    continue
                stock_valid.append(symbol)
                stock = stock.reset_index()
                stock.insert(0,'Symbol',symbol)
                stocks_data = pd.concat([stocks_data, stock])

            stocks_data = stocks_data.reset_index(drop=True)
            stocks_data.columns = ['Symbol','Date','Open_price','High_price','Low_price','Close_price','Adj_close','Volume']
            try:
                stocks_data.to_sql(name, con=engine, if_exists='append', index=False)
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                engine.dispose()
            
        except:
            connection.rollback()

        print('\n')
        print('Invalid Symbol Names: ', ', '.join(stock_invalid))
        print('  Valid Symbol Names: ',', '.join(stock_valid))
        print('Portfolio: \'{}\' Created Successfully......'.format(name))

        # Display portfolio 
        print('\n')
        show = input('Would you like to view the portfolio \'{}\' created just now? (y/n): '.format(name))
        data_show(show)

    except:
        print('errors')
    finally:
        connection.close()
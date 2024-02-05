import mysql.connector
import yfinance as yf
from prettytable import PrettyTable
from sqlalchemy import create_engine
import pandas as pd

# The date range for a specific portfolio
def fetch_date(name):
    date_query = f'select min(Date),max(Date) from {name}'
    cursor = connection.cursor()
    cursor.execute(date_query)
    dates = cursor.fetchall()
    start_date = dates[0][0].strftime("%Y-%m-%d %H:%M:%S")[0:10]
    end_date = dates[0][1].strftime("%Y-%m-%d %H:%M:%S")[0:10]
    cursor.close()
    return start_date, end_date


def stock_add(adds,start_date,end_date):
    if adds == 'no':
        return
    engine = create_engine('mysql+mysqlconnector://root:DSCI560@localhost/yfinance'.format(**db_config))
    stocks_data = pd.DataFrame()
    stock_invalid = []
    stock_valid = []
    stock_list = adds.split(',')
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
    print('\n')
    print('Invalid Stock Symbol: ', ', '.join(stock_invalid))
    print('  Valid Stock Symbol: ',', '.join(stock_valid))
    print('\n')
    print('Valid Stock Added to Portfolio \'{}\' Successfully'.format(name))


def stock_remove(removes):
    if removes == 'no':
        return
    cursor = connection.cursor()
    stock_list = removes.split(',')
    for r in stock_list:
        delete_query = f"DELETE FROM {name} WHERE Symbol = '{r}'"
        try:
            cursor.execute(delete_query)
        except Exception as e:
            print(f"An error occurred: {e}")
    connection.commit()
    print('Stock Deleted from Portfolio \'{}\' Successfully'.format(name))


    
def show():
    try:
        print('Current portfolios are listed below:')
        print('\n')
        cursor = connection.cursor()
        name_createTime_query = f"SELECT table_name, create_time FROM information_schema.tables WHERE table_schema = '{database}'"
        cursor.execute(name_createTime_query)
        tables = cursor.fetchall()
        tables_names = [i[0] for i in tables]
        tables_createTime = [item[1].strftime("%Y-%m-%d %H:%M:%S") for item in tables]
        for i in range(len(tables_names)):
            port_name = tables_names[i]
            print('Portfolio Name: ',port_name)
            # get stock list
            # check if portfolio is empty
            empty_check_query = f"SELECT COUNT(*) FROM {port_name}"
            cursor.execute(empty_check_query)
            row_count = cursor.fetchone()[0]
            if row_count == 0:
                print('Stock List: the portfolio is empty')
            else:
                cursor.execute(f'select distinct(symbol) from {port_name}')
                stocks = cursor.fetchall()
                stock_list = [item[0] for item in stocks]
                print('Stock List: ', ', '.join(stock_list))
            print('Creation Time: ', tables_createTime[i])
            print('\n')

        cursor.close()
    except Exception as e:
        print(e)


if __name__ == '__main__':

    print('-------------------CREATING PORTFOLIOS------------------')
    print('Functions Including:')
    print('1.Add stock to portfolio')
    print('2.Remove stock from portfolio')
    print('3.Display portfolios information')
    print('\n')
    print('-------------------LET\'S GET STARTED-------------------')
    # connect to database
    db_config = {
        'host' : 'localhost',
        'user' : 'root',
        'password' : 'DSCI560',
        'database' :'yfinance',
    }
    database = 'yfinance'
    connection = mysql.connector.connect(**db_config)
    try:
        show()
        name = input('Please enter the portfolio name wish to manage: ')

        adds = input('Please enter the list of stocks to be added(split by \',\'), skip by entering \'no\': ')
        # fetch start and end date for the portfolio selected
        start_date, end_date = fetch_date(name)
        stock_add(adds,start_date, end_date)

        removes = input('Please enter the list of stocks to be removed(split by \',\'), skip by entering \'no\': ')
        stock_remove(removes)

        flag = input('Would you like to see the detail of the portfolios again( y/n): ')
        if flag == 'y':
            show()
        else:
            print('\n')
            print('End of portfolios management')
    except:
        print('errors')
    finally:
        connection.close()
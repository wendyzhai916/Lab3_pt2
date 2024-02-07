import pandas as pd
import numpy as np

def moving_average(data):
    '''
    Returns a pandas dataframe with two columns, Buy and Sell
    If buy on the date, value will be the closing price. Otherwise NA
    If sell on the date, value will be the closing price. Otherwise NA
    '''
    data['MA20'] = data['Close'].rolling(window=20).mean() # moving average of 20 days
    data['MA50'] = data['Close'].rolling(window=50).mean() # moving average of 50 days
    data['Signal'] = np.where(data['MA20']>data['MA50'],1,0) 
    data['Position'] = data['Signal'].diff()
    data['Buy'] = np.where(data['Position'] == 1, data['Close'], np.NAN)
    data['Sell'] = np.where(data['Position'] == -1, data['Close'], np.NAN)
    return data[['Buy','Sell']]

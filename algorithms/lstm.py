import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def load_portfolio(engine):
    query = "SELECT Date, Close_price FROM portfolio_data"
    portfolio_data = pd.read_sql(query, engine)
    portfolio_data['Date'] = pd.to_datetime(portfolio_data['Date'])
    portfolio_data.set_index('Date', inplace=True)
    return portfolio_data

def create_dataset(data, time_steps):
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(data[i:(i + time_steps), 0])
        y.append(data[i + time_steps, 0])
    return np.array(X), np.array(y)

def create_buy_sell_df(data_dates, predictions):
    df = pd.DataFrame(index=data_dates, columns=["Buy", "Sell"])
    df["Buy"] = np.nan
    df["Sell"] = np.nan
    for i in range(len(predictions)):
        if i % 2 == 0:
            df.iloc[i]["Buy"] = predictions[i]
        else:
            df.iloc[i]["Sell"] = predictions[i]
    return df

def lstm():
    train_size = int(len(portfolio_data) * 0.8)
    train_data, test_data = portfolio_data[:train_size], portfolio_data[train_size:]

    scaler = MinMaxScaler()
    train_data_scaled = scaler.fit_transform(train_data)
    test_data_scaled = scaler.transform(test_data)

    time_steps = 60
    X_train, y_train = create_dataset(train_data_scaled, time_steps)
    X_test, y_test = create_dataset(test_data_scaled, time_steps)

    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=100, batch_size=32)

    predictions = model.predict(X_test)
    predictions = scaler.inverse_transform(predictions)
    y_test = scaler.inverse_transform(y_test.reshape(-1, 1))
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print('Root Mean Squared Error (RMSE):', rmse)

    x_input = test_data_scaled[-time_steps:].reshape(1, -1)
    temp_input = list(x_input)
    temp_input = temp_input[0].tolist()

    future_predictions = []
    n_future = 30
    for i in range(n_future):
        if len(temp_input) > time_steps:
            x_input = np.array(temp_input[1:])
            x_input = x_input.reshape(1, -1)
            x_input = x_input.reshape((1, time_steps, 1))
            yhat = model.predict(x_input, verbose=0)
            temp_input.extend(yhat[0].tolist())
            temp_input = temp_input[1:]
            future_predictions.append(yhat[0][0])
        else:
            x_input = x_input.reshape((1, time_steps, 1))
            yhat = model.predict(x_input, verbose=0)
            temp_input.extend(yhat[0].tolist())
            future_predictions.append(yhat[0][0])

    print('Future Predictions:', future_predictions)

    future_dates = pd.date_range(start=test_data.index[-1], periods=n_future+1)[1:]
    future_df = create_buy_sell_df(future_dates, future_predictions)
    return future_df

import numpy as np
import pandas as pd
import mysql.connector
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error

def load_portfolio():
    query = "SELECT Date, Close_price FROM portfolio_data"
    portfolio_data = pd.read_sql(query, engine)
    portfolio_data['Date'] = pd.to_datetime(portfolio_data['Date'])
    portfolio_data.set_index('Date', inplace=True)

train_size = int(len(data) * 0.8)
train_data, test_data = data[:train_size], data[train_size:]

scaler = MinMaxScaler()
train_data_scaled = scaler.fit_transform(train_data)
test_data_scaled = scaler.transform(test_data)

def create_dataset(data, time_steps):
    X, y = [], []
    for i in range(len(data) - time_steps):
        X.append(data[i:(i + time_steps), 0])
        y.append(data[i + time_steps, 0])
    return np.array(X), np.array(y)

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

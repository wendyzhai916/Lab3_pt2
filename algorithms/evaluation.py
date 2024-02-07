import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

def evaluation_metrics(price_pred, price_true):
    MAE = mean_absolute_error(price_true, price_pred)
    RMSE = np.sqrt(price_true, price_pred)
    R2 = r2_score(price_true, price_pred)
    print("Model Evaluations:")
    print("Mean Absolute Error: {}".format(MAE))
    print("Root Mean Squared Error: {}".format(RMSE))
    print("R squared: {}".format(R2))

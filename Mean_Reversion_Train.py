import yfinance as yf
import math
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import os
import shutil
from util import *



time_effect1 = lambda L, x: 1-(x/L)
time_effect2 = lambda L, x: L/(x+L)
time_effect3 = lambda L, x: (-1/(L**2))(x**2)+1
time_effect3 = lambda L, x: -1/((x-L)**2)


def train(MODEL_PATH, training_prices, MAX_HOLDING=100):
    answer = []
    for pos1 in range(len(training_prices) - MAX_HOLDING):
        ans = 0
        for pos2 in range(1, MAX_HOLDING):
            ans += (training_prices.iloc[pos1 + pos2] - training_prices.iloc[pos1]) * time_effect1(MAX_HOLDING, pos2)
        answer.append(ans)

    answer = normalize_average(answer)

    sma10 = get_sma(prices, 10)
    sma30 = get_sma(prices, 20)
    sma50 = get_sma(prices, 50)
    sma100 = get_sma(prices, 100)
    sd10 = get_sd(prices, 10)
    sd30 = get_sd(prices, 20)
    sd50 = get_sd(prices, 50)
    sd100 = get_sd(prices, 100)

    LONGEST_SMA = 100
    if MAX_HOLDING < LONGEST_SMA:
        answer = answer[LONGEST_SMA - MAX_HOLDING:]

    x = []
    y = []
    for pos in range(0, len(prices) - LONGEST_SMA):
        x.append([sma10[pos], sma30[pos], sma50[pos], sma100[pos], sd10[pos], sd30[pos], sd50[pos], sd100[pos]])
        ans = (answer[pos] + 1) / 2
        y.append(ans)
    x = np.array(x)
    y = np.array(y)
    prices = prices[MAX_HOLDING - LONGEST_SMA:len(prices) - MAX_HOLDING]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2)

    def create_model():
        return tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(8,), name='layers_flatten'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(1),
    ])

    model = create_model()
    model.compile(optimizer='adam',
                loss='mean_absolute_error',)
    
    model.fit(x=x_train, 
          y=y_train, 
          epochs=50, 
          validation_data=(x_test, y_test), 
        )
    return model
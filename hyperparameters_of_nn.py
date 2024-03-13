# -*- coding: utf-8 -*-
pip install -U keras-tuner

from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import utils
from google.colab import files
from kerastuner.tuners import RandomSearch, Hyperband, BayesianOptimization
import numpy as np

(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)
x_train = x_train / 255
x_test = x_test / 255
y_train = utils.to_categorical(y_train, 10)
y_test = utils.to_categorical(y_test, 10)

def build_model(hp):
    model = Sequential()
    activation_choice = hp.Choice('activation', values=['relu', 'sigmoid', 'tanh', 'elu', 'selu'])
    model.add(Dense(units=hp.Int('units_input',    # Полносвязный слой с разным количеством нейронов на входном слое
                                   min_value=16,   # минимальное количество нейронов - 16
                                   max_value=32,   # максимальное количество - 32
                                   step=4),        # шаг проверки нейронов
                    input_dim=784,
                    activation=activation_choice)) # Выбираем функцию активации из предложенных 5
    model.add(Dense(units=hp.Int('units_hidden',   # Кол-во нейронов на скрытом слое
                                   min_value=8,
                                   max_value=24,
                                   step=4),
                    activation=activation_choice))
    model.add(Dense(10, activation='softmax'))     # функция активации
    model.compile(                                 # функция созд модели
        optimizer=hp.Choice('optimizer', values=['adam','rmsprop','SGD']), # выбор оптимизаторов из 3 предложенных
        loss='categorical_crossentropy',           # ошибка
        metrics=['accuracy'])                      # метрика точности
    return model

tuner = RandomSearch(
    build_model,                 # функция создания модели
    objective='val_accuracy',    # метрика, которую нужно оптимизировать -
                                 # доля правильных ответов на проверочном наборе данных
    max_trials=25,               # максимальное количество запусков обучения
    directory='test_directory'   # каталог, куда сохраняются обученные сети
    )

tuner.search_space_summary()

tuner.search(x_train,                  # Данные для обучения
             y_train,                  # Правильные ответы
             batch_size=256,           # Размер мини-выборки
             epochs=10,                # Количество эпох обучения
             validation_split=0.2,     # Часть данных, которая будет использоваться для проверки (%)
             )

tuner.results_summary()

models = tuner.get_best_models(num_models=3)

for model in models:
  model.summary()
  model.evaluate(x_test, y_test) #оценка по набору данных, которые не использовались в обучении
  print()

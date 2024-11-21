import os
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn import svm

TRAIN_DIR = "./train"
os.path.exists(TRAIN_DIR) or os.makedirs(TRAIN_DIR)

t_data = pd.read_csv("training_data.csv")
ranking = t_data.loc[:, t_data.columns[t_data.columns != "Viscosity"]].describe().transpose().sort_values("std").index.to_numpy()[:400]

rsqs = np.zeros(ranking.shape)

# Wybór modelu
for n in range(len(ranking)):
    y = t_data["Viscosity"].to_numpy()
    X = t_data.loc[:, ranking[:(n+1)]].to_numpy()

    kf = KFold(n_splits=5)
    scores = np.zeros((5,))

    for i, (train_ind, test_ind) in enumerate(kf.split(X)):
        train_X = X[np.array(train_ind), :]
        train_y = y[np.array(train_ind)]
        test_X = X[np.array(test_ind)]
        test_y = y[np.array(test_ind)]

        clf = svm.SVR().fit(train_X, train_y)
        scores[i] = (clf.score(test_X, test_y))

    rsqs[n] = scores.mean()

rsqs.save(f"{TRAIN_DIR}/parameter_selection.npy")

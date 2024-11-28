import os
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.feature_selection import r_regression, SequentialFeatureSelector
from sklearn import svm
import math

TRAIN_DIR = "./train"
os.path.exists(TRAIN_DIR) or os.makedirs(TRAIN_DIR)

t_data = pd.read_csv("training_data.csv")
print(t_data.shape)
ranking = t_data.loc[:, t_data.columns[t_data.columns != "Viscosity"]].describe().transpose().sort_values("std").index.to_numpy()[:500]
correlation = t_data.loc[:, t_data.columns[t_data.columns != "Viscosity"]].corr() > 0.5

print("correlation:", correlation.shape)
features_to_drop = []

for i, j in [(i, j) for i in range(0, correlation.shape[0]) for j in range(0, i)]:
        if correlation.iloc[i, j]:
            rsqa, rsqb = r_regression(t_data.iloc[:, [i, j]], t_data["Viscosity"])
            if abs(rsqa) > abs(rsqb): features_to_drop.append(i)
            else: features_to_drop.append(j)

t_data = t_data.loc[:, [not i in features_to_drop for i in range(0, t_data.shape[1])]]

print(t_data.shape)
exit(0)

rsqs = np.zeros(ranking.shape)

# Wybór parametrów
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

print(rsqs.shape)
np.save(f"{TRAIN_DIR}/parameter_selection.npy", rsqs)

print("finished!\a")

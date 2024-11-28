import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import r_regression, SequentialFeatureSelector
from sklearn import svm
import math

TRAIN_DIR = "./train"
os.path.exists(TRAIN_DIR) or os.makedirs(TRAIN_DIR)

if not os.path.exists(f"{TRAIN_DIR}/data_after_correaltion.csv"):
    t_data = pd.read_csv("training_data.csv")
    print(t_data.shape)
    correlation = t_data.loc[:, t_data.columns[t_data.columns != "Viscosity"]].corr() > 0.5

    print("correlation:", correlation.shape)
    features_to_drop = []

    for i, j in [(i, j) for i in range(0, correlation.shape[0]) for j in range(0, i)]:
            if correlation.iloc[i, j]:
                rsqa, rsqb = r_regression(t_data.iloc[:, [i, j]], t_data["Viscosity"])
                if abs(rsqa) > abs(rsqb): features_to_drop.append(i)
                else: features_to_drop.append(j)

    t_data = t_data.loc[:, [not i in features_to_drop or t_data.columns[i] == "Viscosity" for i in range(0, t_data.shape[1])]]
    t_data.to_csv(f"{TRAIN_DIR}/data_after_correaltion.csv")
else:
    t_data = pd.read_csv(f"{TRAIN_DIR}/data_after_correaltion.csv")

print(t_data.shape)

rsqs = list()

y = t_data["Viscosity"]
X = t_data.loc[:, t_data.columns[t_data.columns != "Viscosity"]]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42)

# Wybór parametrów
for n in range(1, t_data.shape[1]-1):
    selected = SequentialFeatureSelector(
            svm.SVR(), n_features_to_select = n, cv = 5, n_jobs = -1
            ).fit(X_train, y_train)

    clf = svm.SVR().fit(X_train[selected.get_feature_names_out()], y_train)
    rsqs.append(clf.score(X_test[selected.get_feature_names_out()], y_test))
    np.save(f"{TRAIN_DIR}/parameter_selection_iter{n}.npy", rsqs)

print(len(rsqs))
np.save(f"{TRAIN_DIR}/parameter_selection.npy", rsqs)

print("finished!\a")

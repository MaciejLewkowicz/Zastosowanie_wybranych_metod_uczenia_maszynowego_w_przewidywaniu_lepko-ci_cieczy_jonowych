import os
import matplotlib.pyplot as plt
import numpy as np
import data

PLOT_DIR = "./plots"
os.path.exists(PLOT_DIR) or os.makedirs(PLOT_DIR)

# histogram z ciśnieniem
t_data = data.get_data()

fig, ax = plt.subplots()

ax.hist(t_data[90 < t_data["Pressure"]][t_data["Pressure"] < 200]["Pressure"], bins = 100)

plt.savefig(f"{PLOT_DIR}/histogram.png")

# wybór ilości parametrów
rsqs = np.load("./train/parameter_selection.npy")

fix, ax = plt.subplots()

ax.plot(np.arange(1, len(rsqs)+1), rsqs, 'o')

plt.savefig(f"{PLOT_DIR}/parameters_selection.png")

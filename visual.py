import matplotlib.pyplot as plt
import data

PLOT_DIR = "./plots"
os.path.exists(PLOT_DIR) or os.makedirs(PLOT_DIR)

t_data = data.get_data()

fig, ax = plt.subplots()

ax.hist(t_data[90 < t_data["Pressure"]][t_data["Pressure"] < 200]["Pressure"], bins = 100)

plt.savefig(f"{PLOT_DIR}/histogram.png")

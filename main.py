import pandas as pd
import ilthermopy as ilt


def main():
    if not os.path.exists("ilthermo.data.csv"):
        search = ilt.Search(n_compounds = 1, prop = "Viscosity")
        search.to_csv("ilthermo.data.csv")
    else:
        search = pd.read_csv("ilthermo.data.csv")

    os.path.exists("./data") or os.makedirs("./data")

    for idx in search.id.iloc:
        if not os.path.exists(f"./data/{idx}.csv"):
            entry = ilt.GetEntry(idx)
            entry.data.to_csv(f"./data/{idx}.csv")
        print(f"got entry for {idx}")

    print('finished\a')
    return 0

if __name__ == "__main__":
    exit(main())

import pandas as pd
import ilthermopy as ilt


def main():
    if not os.path.exists("ilthermo.data.csv"):
        search = ilt.Search(n_compounds = 1, prop = "Viscosity")
        search.to_csv("ilthermo.data.csv")
    else:
        search = pd.read_csv("ilthermo.data.csv")

    os.path.exists("./data") or os.makedirs("./data")

    data = search[["id", "cmp1", "cmp1_smiles", "reference"]].copy()

    data["raw_data"] = None

    ids = []
    data_sets = []

    for idx in data.id.iloc:
        data_entry = None

        if not os.path.exists(f"./data/{idx}.csv"):
            entry = ilt.GetEntry(idx)
            data_entry = entry.data.rename(entry.header, axis="columns")
            data_entry.to_csv(f"./data/{idx}.csv")
        else:
            data_entry = pd.read_csv(f"./data/{idx}.csv")

        data_sets.append(data_entry)
        ids.append(idx)


    data.update(pd.DataFrame({"id": ids,
                              "raw_data": data_sets}))

    print('finished\a')
    return 0

if __name__ == "__main__":
    exit(main())

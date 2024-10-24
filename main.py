import pandas as pd
import ilthermopy as ilt
import os

def get_ions(data):
    anions = []
    cations = []
    for cmp in data["cmp1_smiles"].iloc:
        anions.append(cmp.split('.')[0])
        cations.append(cmp.split('.')[1])
    return (list(set(anions)), list(set(cations)))

def count_datapoints(data):
    dp_count = 0
    for dset in data["raw_data"].iloc:
        dp_count += dset.shape[0]
    return dp_count

def count_datasets(data):
    return data.shape[0]

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

    print(f"Anions count: {len(get_ions(data)[0])}")
    print(f"Cations count: {len(get_ions(data)[1])}")
    print(f"Dataset count: {count_datasets(data)}")
    print(f"Datapoint count: {count_datapoints(data)}")

    print('finished\a')
    return 0

if __name__ == "__main__":
    exit(main())

import pandas as pd
import ilthermopy as ilt
import os
import io
import padelpy

DATA_DIR = "./data"

def get_data():
    os.path.exists(DATA_DIR) or os.makedirs(DATA_DIR)

    if not os.path.exists(f"{DATA_DIR}/data.csv"):
        if not os.path.exists(f"{DATA_DIR}/ilthermo.data.csv"):
            search = ilt.Search(n_compounds = 1, prop = "Viscosity")
            search.to_csv(f"{DATA_DIR}/ilthermo.data.csv")
        else:
            search = pd.read_csv(f"{DATA_DIR}/ilthermo.data.csv")


        data = search[["id", "cmp1", "cmp1_smiles", "reference"]].copy()

        data["raw_data"] = None

        ids = []
        data_sets = []

        for idx in data.id.iloc:
            data_entry = None

            if not os.path.exists(f"{DATA_DIR}/{idx}.csv"):
                entry = ilt.GetEntry(idx)
                data_entry = entry.data.rename(entry.header, axis="columns")
                data_entry.to_csv(f"{DATA_DIR}/{idx}.csv")
            else:
                data_entry = pd.read_csv(f"{DATA_DIR}/{idx}.csv")

            data_sets.append(data_entry)
            ids.append(idx)


        data.update(pd.DataFrame({"id": ids,
                                  "raw_data": data_sets}))

        data_to_save = data.copy()
        data_csvs = []

        for raw in data["raw_data"].iloc:
            data_csvs.append(raw.to_csv().replace("\n", ";"))

        data_to_save.update(pd.DataFrame({ "raw_data": data_csvs }))
        data_to_save.to_csv(f"{DATA_DIR}/data.csv")
    else:
        data = pd.read_csv(f"{DATA_DIR}/data.csv")
        raw_frames = []
        for raw in data["raw_data"].iloc:
            raw_frames.append(pd.read_csv(io.StringIO(raw.replace(";","\n"))))
        data.update(pd.DataFrame({ "raw_data": raw_frames }))

    return data


    data["raw_data"] = None

    ids = []
    data_sets = []

    return d_cations, d_anions

def get_ions(data) -> tuple[list[str], list[str]]:
    anions = []
    cations = []
    for cmp in data["cmp1_smiles"].iloc:
        anions.append(cmp.split('.')[0])
        cations.append(cmp.split('.')[1])
    return (list(set(cations)), list(set(anions)))

def count_datapoints(data) -> int:
    dp_count = 0
    for dset in data["raw_data"].iloc:
        dp_count += dset.shape[0]
    return dp_count

def count_datasets(data) -> int:
    return data.shape[0]

def main() -> int:
    data = get_data()

    print(f"Anions count: {len(get_ions(data)[1])}")
    print(f"Cations count: {len(get_ions(data)[0])}")
    print(f"Dataset count: {count_datasets(data)}")
    print(f"Datapoint count: {count_datapoints(data)}")

    print('finished\a')
    return 0

if __name__ == "__main__":
    exit(main())

import pandas as pd
import ilthermopy as ilt
import os
import io
import padelpy

DATA_DIR = "./data"

# TODO: Zrobić żeby używało tylko jednej linii
def print_status(cur, max, msg):
    progress = int(cur/max*10)
    print("[", end="")
    print("-"*progress, end="")
    print(" "*(10-progress), end="")
    print("]", end="")
    print(f" {int(cur/max*100):3}%", end="")

    if not msg is None:
        print(f" {msg}", end="")

    print()

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

        print("getting datasets:")
        for i, idx in enumerate(data.id.iloc):
            data_entry = None
            print_status(i, data.shape[0], str(idx))

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

def get_ion_descriptors(ion_codes) -> pd.DataFrame:
    d_ions: pd.DataFrame = None

    if not os.path.exists(f"{DATA_DIR}/d_ions.csv"):
        print("generating ion descriptors:")
        d_list = list()
        for i, code in enumerate(ion_codes):
            print_status(i, len(ion_codes)-1, code)
            descriptors = dict()
            try:
                descriptors = padelpy.from_smiles(code)
            except KeyboardInterrupt as e:
                raise e
            except:
                print(f"failed to compute descriptors for {code}")
                descriptors = None
            d_list.append((code, descriptors))
        d_ions = pd.DataFrame(d_list)
        d_ions.to_csv(f"{DATA_DIR}/d_ions.csv")
    else:
        d_ions = pd.read_csv(f"{DATA_DIR}/d_ions.csv")

    return d_ions

def get_ions(data) -> tuple[list[str]]:
    ions = []
    for cmp in data["cmp1_smiles"].iloc:
        ions.append(cmp.split('.')[0])
        ions.append(cmp.split('.')[1])
    return list(set(ions))

def count_datapoints(data) -> int:
    dp_count = 0
    for dset in data["raw_data"].iloc:
        dp_count += dset.shape[0]
    return dp_count

def count_datasets(data) -> int:
    return data.shape[0]

def main() -> int:
    data = get_data()

    print(f"Ions count: {len(get_ions(data))}")
    print(f"Dataset count: {count_datasets(data)}")
    print(f"Datapoint count: {count_datapoints(data)}")

    d_ions = get_ion_descriptors(get_ions(data))

    print('finished\a')
    return 0

if __name__ == "__main__":
    exit(main())

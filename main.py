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

        data_points = {"id":[],
                       "Temperature": [],
                       "Viscosity": [],
                       "Error of viscosity": []}

        print("getting datasets:")
        for i, idx in enumerate(data.id.iloc):
            data_set = None
            print_status(i, data.shape[0]-1, str(idx))

            os.path.exists(f"{DATA_DIR}/data_sets") or os.makedirs(f"{DATA_DIR}/data_sets")
            if not os.path.exists(f"{DATA_DIR}/data_sets/{idx}.csv"):
                entry = ilt.GetEntry(idx)
                columns = {x: y.split(',')[0] for x, y in entry.header.items()}
                data_set = entry.data.rename(columns, axis="columns")
                data_set.to_csv(f"{DATA_DIR}/data_sets/{idx}.csv")
            else:
                data_set = pd.read_csv(f"{DATA_DIR}/data_sets/{idx}.csv")

            if not "Viscosity" in data_set.columns.values:
                continue

            data_points["Temperature"] += data_set["Temperature"].values.tolist()
            data_points["Viscosity"] += data_set["Viscosity"].values.tolist()
            data_points["Error of viscosity"] += data_set["Error of viscosity"].values.tolist()
            data_points["id"] += [idx for _ in range(data_set.shape[0])]

        data = data.merge(pd.DataFrame(data_points), on="id", how="left")

        data.to_csv(f"{DATA_DIR}/data.csv")
    else:
        data = pd.read_csv(f"{DATA_DIR}/data.csv")

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
        d_ions = pd.DataFrame({"smiles": d_list[0], "descriptors": d_list[1]})
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
    return data.shape[0]

def count_datasets(data) -> int:
    return len(set(data["id"].iloc))

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

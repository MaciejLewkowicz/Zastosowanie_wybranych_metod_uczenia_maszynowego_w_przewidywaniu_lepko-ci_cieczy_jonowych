import pandas as pd
import ilthermopy as ilt
import os
import io
import padelpy
import math
from rdkit import Chem
from rdkit.Chem import AllChem
from descriptor_list import descriptor_list
import sklearn.preprocessing as prep

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
                       "Pressure": [],
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

            if not "Pressure" in data_set.columns.values:
                data_points["Pressure"] += [None for _ in range(data_set.shape[0])]
            else:
                data_points["Pressure"] += data_set["Pressure"].values.tolist()

            data_points["Temperature"] += data_set["Temperature"].values.tolist()
            data_points["Viscosity"] += data_set["Viscosity"].values.tolist()
            data_points["Error of viscosity"] += data_set["Error of viscosity"].values.tolist()
            data_points["id"] += [idx for _ in range(data_set.shape[0])]

        data = data.merge(pd.DataFrame(data_points), on="id", how="left")

        data.to_csv(f"{DATA_DIR}/data.csv")
    else:
        print("Dataset read from file")
        data = pd.read_csv(f"{DATA_DIR}/data.csv")

    return data

def get_ion_descriptors(ion_codes) -> pd.DataFrame:
    d_ions: pd.DataFrame = None

    if not os.path.exists(f"{DATA_DIR}/d_ions.csv"):
        print("generating ion descriptors:")
        d_dict = {x: [] for x in (descriptor_list + ["smiles"]) }

        for i, code in enumerate(ion_codes):
            print_status(i, len(ion_codes)-1, code)
            descriptors = None
            try:
                descriptors = padelpy.from_smiles(code)
            except KeyboardInterrupt as e:
                raise e
            except:
                print(f"failed to compute descriptors for {code}")
                descriptors = None
            d_dict["smiles"].append(code)
            for item in descriptor_list:
                d_dict[item].append(descriptors[item] if not descriptors is None else None)
        d_ions = pd.DataFrame(d_dict)
        d_ions.to_csv(f"{DATA_DIR}/d_ions.csv")
    else:
        print("Ion descriptors read from file")
        d_ions = pd.read_csv(f"{DATA_DIR}/d_ions.csv")

    return d_ions

def prepare_data(data, d_ions, sum_f):
    print("preparing training data")
    t_data = {x: [] for x in (["Viscosity"] + descriptor_list)}
    i = 0

    for record in data.itertuples():
        ions = record.cmp1_smiles.split('.')
        if len(ions) > 2: continue
        t_data["Viscosity"].append(math.log(record.Viscosity))
        ion1, ion2 = ions
        d_ion1 = d_ions[d_ions['smiles'] == ion1].to_dict("list")
        d_ion2 = d_ions[d_ions['smiles'] == ion2].to_dict("list")
        for desc in descriptor_list:
            desc1 = d_ion1[desc][0]
            desc2 = d_ion2[desc][0]
            if desc1 is None or desc2 is None:
                t_data[desc].append(None)
            else:
                t_data[desc].append(sum_f(desc1, desc2))

    o_data = pd.DataFrame(t_data)
    o_data.dropna(thresh=5, inplace=True)
    o_data.dropna(axis=1, inplace=True)

    o_data = pd.DataFrame(prep.StandardScaler().fit_transform(o_data), columns=o_data.columns)

    filter = o_data.describe().transpose().query("(not min==max) and std > 0.3 and min >= -3 and max <= 3").transpose().columns
    o_data = o_data[filter.tolist() + ["Viscosity"]]

    return o_data

def make_mol_files(ions):
    os.path.exists(f"{DATA_DIR}/mol_files") or os.makedirs(f"{DATA_DIR}/mol_files")
    os.path.exists(f"{DATA_DIR}/mol_files/2d") or os.makedirs(f"{DATA_DIR}/mol_files/2d")
    os.path.exists(f"{DATA_DIR}/mol_files/3d") or os.makedirs(f"{DATA_DIR}/mol_files/3d")

    import base64
    for ion in ions:
        file_name = base64.b64encode(bytes(ion, 'utf-8')).decode("utf-8")
        
        mol = Chem.MolFromSmiles(ion)
        mol = AllChem.AddHs(mol)
        mol.SetProp("_Name", ion)

        if not os.path.exists(f"{DATA_DIR}/mol_files/2d/{file_name}.mol"):
            Chem.MolToMolFile(mol, f"{DATA_DIR}/mol_files/2d/{file_name}.mol")

        if not os.path.exists(f"{DATA_DIR}/mol_files/3d/{file_name}.mol"):
            params = AllChem.ETKDGv3()
            params.randomSeed = 0xf00d
            AllChem.EmbedMolecule(mol, params)
            Chem.MolToMolFile(mol, f"{DATA_DIR}/mol_files/3d/{file_name}.mol")

def get_ions(data) -> tuple[list[str]]:
    ions = []
    for cmp in data["cmp1_smiles"].iloc:
        ions += cmp.split('.')
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

    data_in_temperature = data.query("Temperature==298.15 & Pressure == 101.325")

    d_ions = get_ion_descriptors(get_ions(data))
    t_data = prepare_data(data_in_temperature, d_ions, lambda x, y: x+y)
    t_data.to_csv("training_data.csv")

    # make_mol_files(get_ions(data))

    print('finished\a')
    return 0

if __name__ == "__main__":
    exit(main())

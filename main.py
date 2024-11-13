import pandas as pd
import ilthermopy as ilt


def main():
    search = ilt.Search(n_compounds = 1, prop = "Viscosity")
    search.to_csv("ilthermo.data.csv")
    print()
    return 0

if __name__ == "__main__":
    exit(main())

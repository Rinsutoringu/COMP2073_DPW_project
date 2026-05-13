from pathlib import Path

import pandas as pd

RAW_CSV = Path("archive") / "pokemon.csv"


def main():
    df = pd.read_csv(RAW_CSV)

    print("first 5 rows:")
    print(df.head())

    print("\nlast 5 rows:")
    print(df.tail())

    print("\ninfo:")
    print(df.info())

    print("\ndescribe:")
    print(df.describe())

    print(f"\nshape: {df.shape}")
    print(f"columns: {df.columns.tolist()}")

    print("\nnull counts:")
    print(df.isnull().sum())


if __name__ == "__main__":
    main()

import pandas as pd
raw_csv_path = "archive\\pokemon.csv"

def read_csv(path):
    df = pd.read_csv(path)
    return df
import readcsv

df = readcsv.read_csv(readcsv.raw_csv_path)

# check duplicated rows
if df.duplicated().sum() > 0:
    # delete duplicated rows
    df = df.drop_duplicates()

# fix missing values
print("\n[fill] filling all null values with 'None':\n")
df = df.fillna("None")
print("null values after filling:\n")
print(df.isnull().sum())
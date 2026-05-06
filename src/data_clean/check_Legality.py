import data_clean.readcsv as readcsv

# 检查内容合法性
df = readcsv.read_csv(readcsv.raw_csv_path)
print("get first 5 rows of the data:\n")
print(df.head())

print("\n[check] get last 5 rows of the data:\n")
print(df.tail())

print("\n[check] get the data info:\n")
print(df.info())

print("\n[check] get the data description:\n")
print(df.describe())

print("\n[check] get the data shape, columns and null values:\n")
print(df.shape)

print("\n[check] get the data columns and null values:\n")
print(df.columns.tolist())

print("\n[check] get the data null values:\n")
print(df.isnull().sum())

# null_rows = df.index[df.isnull().any(axis=1)].tolist()
# print(null_rows)


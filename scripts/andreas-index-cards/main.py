import pandas as pd

# Load the Excel file into a pandas DataFrame
df = pd.read_excel('data/TSZ_Stations.xlsx')

# Display the first few rows of the DataFrame
print("First few rows of the DataFrame:")
print(df.head())

# Display basic information about the DataFrame
print("\nDataFrame Info:")
print(df.info())

# Display basic statistics about the numerical columns
print("\nBasic Statistics:")
print(df.describe())

# Display count of non-null values and data types
print("\nColumn Info:")
print(df.dtypes)

# Display the number of unique values in each column
print("\nUnique Values Count:")
print(df.nunique())

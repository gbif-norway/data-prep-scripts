#%%
import pandas as pd
from pathlib import Path
from dbfread import DBF
import json
# %%
orig_input = Path('data/orig/XL')
# %%
orig_dbfs = list(orig_input.glob(r'*[dD][bB][fF]'))
# %%

orig_dbfs
# %%
fmap = {}
for dbf_file in orig_dbfs:
    print(f'reading {dbf_file}')
    dbf = DBF(dbf_file, encoding='iso-8859-1')
    df = pd.DataFrame(iter(dbf))
    fmap[dbf_file.name] = df


# %%
for key, df in fmap.items():
    print(key)
    print(len(df.columns))
    print(df.iloc[:3])
    print('---')
# %%
def categorize_tables(fmap):
    # Define categories based on observed patterns and key columns
    categories = {
        'Geographical Data': ['X', 'Y'],
        'Taxonomic Data': ['TAXA', 'TAXANR', 'GNR', 'GNAVN'],
        'Summary or Auxiliary Data': ['LINJE'],
        'Hierarchical Structure': ['GYLDNR', 'GYLDTAXA'],
        'Update Tracking': ['OPPDATERT', 'MODIF'],
    }

    # Initialize a dictionary to hold categorized tables with their columns
    categorized_tables = {category: {} for category in categories}

    # Additional category for tables that don't fit the above criteria
    categorized_tables['Uncategorized'] = {}

    # Function to check if table columns match category criteria
    def table_matches_category(table, category_columns):
        return all(column in table.columns for column in category_columns)

    # Iterate through the tables and categorize them
    for table_name, df in fmap.items():
        categorized = False
        for category, key_columns in categories.items():
            if table_matches_category(df, key_columns):
                # Store table name with its columns
                categorized_tables[category][table_name] = df.columns.tolist()
                categorized = True
                break  # Stop checking other categories if a match is found

        # If no category matched, mark as uncategorized with its columns
        if not categorized:
            categorized_tables['Uncategorized'][table_name] = df.columns.tolist()

    return categorized_tables

# %%
categorized_tables = categorize_tables(fmap)
# %%
categorized_tables
# %%
with open('categorised.json','w') as f:
    f.write(json.dumps(categorized_tables, indent=4))
# %%
dfs_lst = []
for file_name in categorized_tables['Geographical Data'].keys():
    print(file_name)
    dfs_lst.append(fmap[file_name])
# %%
res = pd.concat(dfs_lst, ignore_index=True, sort=False)
# %%
res.to_csv('xl_folder_concat.csv')
# %%
kriss_dbf = DBF('data/orig/KRYSS.DBF', encoding='iso-8859-1')
# %%
df = pd.DataFrame(iter(kriss_dbf))
# %%

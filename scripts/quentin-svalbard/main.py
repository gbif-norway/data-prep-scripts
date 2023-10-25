#%%
import pandas as pd
import requests
import numpy as np
import urllib
# %%
orig_df = pd.read_excel('/srv/scripts/quentin-svalbard/data/species_to_check.xlsx', sheet_name=None)
# %%
# %%
for marker in orig_df.keys():
    print(marker)
    orig_df[marker]['Marker'] = marker


# %%
merged_df = pd.concat([x for x in orig_df.values()])
# %%
def fetch_gbif_key(row):
    params = {
        'name': row.get('Species', None) or row.get('Genus', None) or row.get('Family', None)
                or row.get('Order', None) or row.get('Class', None) or row.get('Phylum', None)
                or row.get('Domain', None),
        'kingdom': row.get('Domain', None),
        'phylum': row.get('Phylum', None),
        'class': row.get('Class', None),
        'order': row.get('Order', None),
        'family': row.get('Family', None),
        'genus': row.get('Genus', None)
    }
    print(params)
    url = "https://api.gbif.org/v1/species/match"
    response = requests.get(url, params=params)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        return data.get('usageKey', None), data.get('rank', None)
    else:
        return None
# %%
merged_df['GBIF Key', 'Rank'] = merged_df.apply(fetch_gbif_key, axis=1)
# %%
merged_df.loc[merged_df['GBIF Key'].notna(), 'GBIF Key'] = merged_df.loc[merged_df['GBIF Key'].notna(), 'GBIF Key'].astype(int)
merged_df['GBIF Key'] = merged_df['GBIF Key'].astype('Int64')
# %%
fetch_gbif_key(merged_df.iloc[32])
# %%
merged_df['Rank'] = merged_df['GBIF Key', 'Rank'].apply(lambda x: x[1])
# %%
merged_df = merged_df[merged_df.columns.drop(('GBIF Key', 'Rank'))]
# %%
merged_df['GBIF Url'] = merged_df['GBIF Key'].apply(lambda x: f'https://www.gbif.org/species/{x}')
# %%
merged_df.to_csv('/srv/scripts/quentin-svalbard/data/merged_and_clean.csv')
# %%
merged_df = pd.read_csv('/srv/scripts/quentin-svalbard/data/merged_and_clean.csv')
merged_df.loc[merged_df['GBIF Key'].notna(), 'GBIF Key'] = merged_df.loc[merged_df['GBIF Key'].notna(), 'GBIF Key'].astype(int)
merged_df['GBIF Key'] = merged_df['GBIF Key'].astype('Int64')
# %%
merged_df
# %%
def fetch_gbif_occurrences(gbif_key):
    # Define bounding box for Svalbard
    min_lat = 76.4402
    min_long = 10.4866
    max_lat = 80.8224
    max_long = 33.6324

    # Create WKT Polygon string for bounding box
    wkt_polygon = f"POLYGON(({min_long} {min_lat}, {max_long} {min_lat}, {max_long} {max_lat}, {min_long} {max_lat}, {min_long} {min_lat}))"

    params = {
        'taxonKey': gbif_key,
        'geometry': wkt_polygon,
        'limit': 0  # set limit to 0 to get just the count, not the actual data
    }

    url = "https://api.gbif.org/v1/occurrence/search"
    response = requests.get(url, params=params)

    count = None
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)

    # URL encode the WKT polygon string
    encoded_wkt_polygon = urllib.parse.quote(wkt_polygon)

    # Construct GBIF portal URL
    portal_url = f"https://www.gbif.org/occurrence/search?taxon_key={gbif_key}&geometry={encoded_wkt_polygon}"

    return count, portal_url
# %%
result = merged_df['GBIF Key'].apply(fetch_gbif_occurrences)
counts, urls = zip(*result)

# %%
merged_df['Count in Svalbard'] = counts
merged_df['Filtered Occurences URL'] = urls
# %%
merged_df['Count in Svalbard'] = merged_df['Count in Svalbard'].astype('Int64')
#%%
merged_df.to_csv('/srv/scripts/quentin-svalbard/data/with_counts.csv')

# %%

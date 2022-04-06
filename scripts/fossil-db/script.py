import pandas as pd
import numpy as np
from helpers import extract_name, extract_date

# From Zenodo 10.5281/zenodo.6417623
# TODO delete Eirik's mapping header row and upload again so it's consistent with what we will get in the future
df = pd.read_excel('fossils-occurrence_2022-02.xlsx', dtype='str')  # Defaults to first sheet

# Drop all rows which have PMO_NR and SUBNO duplicated
df.drop_duplicates(['PMO_NR', 'SUBNO'], inplace=True, ignore_index=True)

# Create a catalogNumber (unique ID) for each row based
df['catalogNumber'] = df['PMO_NR']
df = df[df['catalogNumber'].notna()]  # Drop all records without a catalogNumber/PMO_NR
df.loc[df['SUBNO'].notna(), 'catalogNumber'] += '_' + df[df['SUBNO'].notna()]['SUBNO']  # Append the subnumber
df.drop(['PMO_NR', 'SUBNO'], axis=1, inplace=True)

# Add the occurrenceIDs, which Dag has suggested we make triplets
df['occurrenceID'] = 'NHMO:PMO:' + df['catalogNumber']

# Rename some columns, mostly based on what Eirik did
mapping = {
           'SPECIES': 'specificEpithet', 
           'GENUS': 'genus',
           'OD': 'scientificNameAuthorship', 
           'country_uk': 'country', 
           'Fylke': 'stateProvince',
           'Kommune': 'county',
           #'': 'scientificName',  # These three seem to have been empty in the spreadsheet from Eirik? 
           #'': 'locality',
           #'': 'lithostratigraphicTerms',
           'GRAD_EAST': 'decimalLongitude',
           'GRAD_NORTH': 'decimalLatitude',
           'FINNER': 'dateAndNames',
           'DIVERSE': 'occurrenceRemarks',
           'taxa': 'taxonRemarks'
        }
df.rename(columns=mapping, inplace=True)

# scientificName seems to sometimes have blank strings e.g. '   ' in... Maybe we should do this for all the cols, idk
df['scientificName'] = df['scientificName'].replace(r'^\s+$', np.nan, regex=True)

# Insert taxonRemarks column contents into scientificName column, when we don't have any other info there or in genus or specificEpithet
name_filter = df['specificEpithet'].isna() & df['genus'].isna() & df['scientificName'].isna()
df.loc[name_filter, 'scientificName'] = df.loc[name_filter, 'taxonRemarks']  # 57824 rows affected
len(df[name_filter & df['taxonRemarks'].isna()])  # 2096 rows still without any taxonomic info... I guess that's ok though? We did our best.

# Date/name extraction
df['recordedBy'] = df['dateAndNames'].fillna('').apply(extract_name)
df['eventDate'] = df['dateAndNames'].fillna('').apply(extract_date)
del df['dateAndNames']

import pdb; pdb.set_trace()

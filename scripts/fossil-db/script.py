import pandas as pd
import numpy as np
from helpers import process_dataframe

# From Zenodo 10.5281/zenodo.6417623 or https://zenodo.org/record/6417623
# TODO delete Eirik's mapping header row and upload again so it's consistent with what we will get in the future
ordinary_specimens = process_dataframe(pd.read_excel('fossils-occurrence_2022-02.xlsx', dtype='str'))  # Defaults to first sheet
type_specimens = process_dataframe(pd.read_excel('fossils-types-occurrence_2022-02.xlsx', dtype='str'))

# For type specimens we just need to map the type field
mapping = { 'H': 'holotype',
            'P': 'para (lecto) type',
            'L': 'lectotype',
            'N': 'neotype',
            'S': 'syntype' } 
type_specimens.replace({'typeStatus': mapping}, inplace=True)

all = ordinary_specimens.append(type_specimens, ignore_index=True)

# Minor fix to the lat/longs which are 0, and add basis of record
all.loc[all['decimalLongitude'] == '0', 'decimalLatitude'] = np.nan
all.loc[all['decimalLongitude'] == '0', 'decimalLongitude'] = np.nan
all['basisOfRecord'] = 'FossilSpecimen'

# IPT seems to struggle with the bigger all.txt file, so we split it into multiple
# all.to_csv('all.txt', sep='\t', index=False)
all[0:100000].to_csv('all-part1.txt', sep='\t', index=False)
all[100000:].to_csv('all-part2.txt', sep='\t', index=False)

import pdb; pdb.set_trace()

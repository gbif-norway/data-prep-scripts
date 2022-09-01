import pandas as pd
import numpy as np
import yaml
import re

file_names = ['SHOISTA-ENTRIES-2016-2022_30-08-2022_at_16-17-31.csv', 'KOBIL-1-2016-COLLECTIONS_30-08-2022_at_16-21-37.csv', 'FERN-1-KOBIL_30-08-2022_at_16-20-24.csv', 'HERB-TJ_30-08-2022_at_16-19-14.csv', 'HERBTJ_30-08-2022_at_16-18-38.csv']
with open('mapping.yml') as f:
    mapping = yaml.safe_load(f)

file = file_names[0]
df = pd.read_csv(file, dtype=str, usecols=mapping, encoding='mac_cyrillic')  # Not utf?
df.rename(columns=mapping, inplace=True)

# Standardise to single spaces, remove trailing
df.replace('\s\s+', ' ', regex=True, inplace=True)
df.replace('^\s+', '', regex=True, inplace=True)
df.replace('\s+$', '', regex=True, inplace=True)

# See tests
def standardise_names(names):
    # print(names)
    name_parts = re.split('[\s,;]', names)
    full_names = []
    for n in name_parts:
        if re.match('[A-Z\.]+$', n):
            initials = n.replace('.', '')
            try:
                full_names[-1] += ' ' + '.'.join(initials) + '.'
            except IndexError:
                pass  # :D
        else:
            match = re.search('[A-Z][a-z]+', n)
            if match:
                full_names.append(match.group())
    return ' | '.join(full_names)

# r2 = df.loc[df['recordedBy_2'].notnull(), 'recordedBy_2'].unique()
# rnew = df.loc[df['recordedBy_2'].notnull(), 'recordedBy_2'].apply(standardise_names).unique()
df.loc[df['recordedBy_2'].notnull(), 'recordedBy'] = ' | ' + df.loc[df['recordedBy_2'].notnull(), 'recordedBy_2'].apply(standardise_names)
del df['recordedBy_2']

# Construct dateIdentified
df.loc[:, ['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy']] = df[['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy']].replace('^0\..+$', np.nan, regex=True)
df.loc[:, ['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy']] = df[['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy']].replace('\.?0+$', '', regex=True)
df['dateIdentified'] = df[['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy']].apply(lambda x: x.str.cat(sep='-'), axis=1)
df.drop(['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy'], axis=1, inplace=True)

import pdb; pdb.set_trace()

df.loc[df['minimumElevationInMeters'].isnull() & df['minimumElevationInMeters'].notnull()] =
# Fix image URLs to point to bucket (or PURL?)

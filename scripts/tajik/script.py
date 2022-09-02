import pandas as pd
import numpy as np
import yaml
import re

file_names = {'shoista': 'SHOISTA-ENTRIES-2016-2022_30-08-2022_at_16-17-31.csv',
              'kobil': 'KOBIL-1-2016-COLLECTIONS_30-08-2022_at_16-21-37.csv',
              'fern': 'FERN-1-KOBIL_30-08-2022_at_16-20-24.csv',
              'herbtj1': 'HERB-TJ_30-08-2022_at_16-19-14.csv',
              'herbtj2': 'HERBTJ_30-08-2022_at_16-18-38.csv'}
with open('mapping.yml') as f:
    mapping = yaml.safe_load(f)

dfs = {}
for df_id, file in file_names.items():
    print(df_id)
    df = pd.read_csv(file, dtype=str, usecols=mapping, encoding='mac_cyrillic')  # Not utf?
    df.rename(columns=mapping, inplace=True)

    # Standardise to single spaces, remove trailing
    df.replace('\s\s+', ' ', regex=True, inplace=True)
    df.replace('^\s+', '', regex=True, inplace=True)
    df.replace('\s+$', '', regex=True, inplace=True)

    # Remove empty records
    df.dropna(subset=['catalognumber', 'associatedMedia'], how='all', inplace=True)

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
    df.loc[df['recordedBy_2'].notnull(), 'recordedBy'] += ' | ' + df.loc[df['recordedBy_2'].notnull(), 'recordedBy_2'].apply(standardise_names)
    del df['recordedBy_2']

    # Construct dateIdentified
    df['dateIdentified'] = None
    df.loc[:, ['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy']] = df[['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy']].replace('^0\..+$', np.nan, regex=True)
    df.loc[:, ['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy']] = df[['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy']].replace('\.?0+$', '', regex=True)
    if df['dateIdentified_dd'].any() or df['dateIdentified_mm'].any() or df['dateIdentified_yy'].any():
        df['dateIdentified'] = df[['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy']].apply(lambda x: x.str.cat(sep='-'), axis=1)
    df.drop(['dateIdentified_dd', 'dateIdentified_mm', 'dateIdentified_yy'], axis=1, inplace=True)

    # Elevation
    df.loc[df['maximumElevationInMeters'].isnull() & df['minimumElevationInMeters'].notnull(), 'maximumElevationInMeters'] = df.loc[df['maximumElevationInMeters'].isnull() & df['minimumElevationInMeters'].notnull(), 'minimumElevationInMeters']

    if df.loc[df['associatedMedia'].notnull(), 'associatedMedia'].any():
        df.loc[df['associatedMedia'].notnull(), 'associatedMedia'] = df.loc[df['associatedMedia'].notnull(), 'associatedMedia'].str.replace('D:\\HERB-PHOTO\\', 'https://storage.gbif-no.sigma2.no/img/tajikistan/', regex=False).str.replace('\\', '/').str.replace(' ', '-').str.lower()

    # Add to dict
    df['df_id'] = df_id
    dfs[df_id] = df

all = pd.concat(dfs.values(), ignore_index=True)

# Looking at duplicates
# all['duplicated_catalognumber'] = all.duplicated('catalognumber')
# all['duplicated_img'] = all.duplicated('associatedMedia')
# all.loc[(all['duplicated_catalognumber'] == True) & (all['duplicated_img'] == True), ['catalognumber', 'associatedMedia']]
all.drop_duplicates(subset='catalognumber', inplace=True)
all.drop_duplicates(subset='associatedMedia', inplace=True)
all['possible_duplicates'] = all.duplicated(['day', 'month', 'year', 'family', 'genus', 'specificEpithet'])
all.loc[all['possible_duplicates'], 'recordedBy']
all.to_csv()

import pdb; pdb.set_trace()

import pandas as pd
import numpy as np
import yaml
import re
import difflib

file_names = {'shoista': 'SHOISTA-ENTRIES-2016-2022_30-08-2022_at_16-17-31.csv',
              'kobil': 'KOBIL-1-2016-COLLECTIONS_30-08-2022_at_16-21-37.csv',
              'fern': 'FERN-1-KOBIL_30-08-2022_at_16-20-24.csv',
              'herbtj1': 'HERB-TJ_30-08-2022_at_16-19-14.csv',
              'herbtj2': 'HERBTJ_30-08-2022_at_16-18-38.csv'}
with open('mapping.yml') as f:
    mapping = yaml.safe_load(f)

countries = ['Afghanistan', 'Aland Islands', 'Albania', 'Algeria', 'American Samoa', 'Andorra', 'Angola', 'Anguilla', 'Antarctica', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Aruba', 'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bermuda', 'Bhutan', 'Bolivia, Plurinational State of', 'Bonaire, Sint Eustatius and Saba', 'Bosnia and Herzegovina', 'Botswana', 'Bouvet Island', 'Brazil', 'British Indian Ocean Territory', 'Brunei Darussalam', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia', 'Cameroon', 'Canada', 'Cape Verde', 'Cayman Islands', 'Central African Republic', 'Chad', 'Chile', 'China', 'Christmas Island', 'Cocos (Keeling) Islands', 'Colombia', 'Comoros', 'Congo', 'Congo, The Democratic Republic of the', 'Cook Islands', 'Costa Rica', "Côte d'Ivoire", 'Croatia', 'Cuba', 'Curaçao', 'Cyprus', 'Czech Republic', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Ethiopia', 'Falkland Islands (Malvinas)', 'Faroe Islands', 'Fiji', 'Finland', 'France', 'French Guiana', 'French Polynesia', 'French Southern Territories', 'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Gibraltar', 'Greece', 'Greenland', 'Grenada', 'Guadeloupe', 'Guam', 'Guatemala', 'Guernsey', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Heard Island and McDonald Islands', 'Holy See (Vatican City State)', 'Honduras', 'Hong Kong', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran, Islamic Republic of', 'Iraq', 'Ireland', 'Isle of Man', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jersey', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', "Korea, Democratic People's Republic of", 'Korea, Republic of', 'Kuwait', 'Kyrgyzstan', "Lao People's Democratic Republic", 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Macao', 'Macedonia, Republic of', 'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Martinique', 'Mauritania', 'Mauritius', 'Mayotte', 'Mexico', 'Micronesia, Federated States of', 'Moldova, Republic of', 'Monaco', 'Mongolia', 'Montenegro', 'Montserrat', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands', 'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'Niue', 'Norfolk Island', 'Northern Mariana Islands', 'Norway', 'Oman', 'Pakistan', 'Palau', 'Palestinian Territory, Occupied', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Pitcairn', 'Poland', 'Portugal', 'Puerto Rico', 'Qatar', 'Réunion', 'Romania', 'Russian Federation', 'Rwanda', 'Saint Barthélemy', 'Saint Helena, Ascension and Tristan da Cunha', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Martin (French part)', 'Saint Pierre and Miquelon', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Sint Maarten (Dutch part)', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Georgia and the South Sandwich Islands', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'South Sudan', 'Svalbard and Jan Mayen', 'Swaziland', 'Sweden', 'Switzerland', 'Syrian Arab Republic', 'Taiwan, Province of China', 'Tajikistan', 'Tanzania, United Republic of', 'Thailand', 'Timor-Leste', 'Togo', 'Tokelau', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Turks and Caicos Islands', 'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'United States Minor Outlying Islands', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Venezuela, Bolivarian Republic of', 'Viet Nam', 'Virgin Islands, British', 'Virgin Islands, U.S.', 'Wallis and Futuna', 'Yemen', 'Zambia', 'Zimbabwe']
dfs = {}
for df_id, file in file_names.items():
    print(df_id)
    df = pd.read_csv(file, dtype=str, usecols=mapping, encoding='mac_cyrillic')  # Not utf?
    df.rename(columns=mapping, inplace=True)

    # Standardise to single spaces, remove trailing
    df.replace('\s\s+', ' ', regex=True, inplace=True)
    df.replace('^\s+', '', regex=True, inplace=True)
    df.replace('\s+$', '', regex=True, inplace=True)
    df.replace('^\?$', None, regex=True, inplace=True)
    df.replace('^\?\s*', '', regex=True, inplace=True)

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

    # Collected dates
    df.loc[:, ['day', 'month', 'year']] = df[['day', 'month', 'year']].replace('^0\..+$', np.nan, regex=True)
    df.loc[:, ['day', 'month', 'year']] = df[['day', 'month', 'year']].replace('\.?0+$', '', regex=True)

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
        df.loc[df['associatedMedia'].notnull(), 'associatedMedia'] = df.loc[df['associatedMedia'].notnull(), 'associatedMedia'].str.replace('D:\\HERB-PHOTO\\', 'https://storage.gbif-no.sigma2.no/img/tajikistan/', regex=False).str.replace('\\', '/', regex=False).str.replace(' ', '-', regex=False).str.lower()

    # Fix country spelling mistakes
    df['country'] = df['country'].str.replace('^T$', 'Tajikistan', regex=True)

    def fix_country_spelling(x):
        if x and x is not np.NaN:
            matches = difflib.get_close_matches(x, countries)
            if matches:
                return matches[0]
        return None

    df['country'] = df['country'].apply(fix_country_spelling)
    print(df.loc[~df['country'].isin(countries), 'country'].unique())

    # Add to dict
    df['df_id'] = df_id
    dfs[df_id] = df

all = pd.concat(dfs.values(), ignore_index=True)
all['basisofrecord'] = 'PreservedSpecimen'

# Looking at duplicates
# all['duplicated_catalognumber'] = all.duplicated('catalognumber')
# all['duplicated_img'] = all.duplicated('associatedMedia')
# all.loc[(all['duplicated_catalognumber'] == True) & (all['duplicated_img'] == True), ['catalognumber', 'associatedMedia']]
all.drop_duplicates(subset='catalognumber', inplace=True)
all.drop_duplicates(subset='associatedMedia', inplace=True)
# all['possible_duplicates'] = all.duplicated(['day', 'month', 'year', 'family', 'genus', 'specificEpithet'])
# all.loc[all['possible_duplicates'], 'recordedBy']
all = all[all['catalognumber'].notna()]
all = all[all['family'].notna()]
all['occurrenceID'] = 'urn:catalog:HERB:' + all['catalognumber']

all.to_csv('all.csv', index=False, encoding='utf8')


import pdb; pdb.set_trace()

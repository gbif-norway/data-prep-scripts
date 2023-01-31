import pandas as pd
from dateutil import parser
import utm
#from pyproj import Proj

df = pd.read_csv('Rock type_ Table.txt', sep=';', dtype='str', quotechar='"', encoding='utf-8')

mapping = {
    'CAT_NO': 'catalogNumber',
    'ROCK_NA': 'scientificName',
    'NO_NA': 'vernacularName',
    'SYNONYM': 'genericName',
    'ASSOC': 'lithostratigraphicTerms',
    'COUNTRY': 'country',
    'MUNICIPALITY': 'municipality',
    'LOCALITY': 'locality',
    'LOC_DETAILS': 'locality',
    'COLLECTION': 'verbatimEventDate',
    'ACQUIRED': 'eventRemarks',
    'COLLECTOR': 'recordedBy',
    #'OLD STORED': '',
    #'NEW STORED': '',
    'REMARKS': 'occurrenceRemarks',
    'TOPONYMY': 'verbatimLocality',
    'UPDATED': 'modified',
    #'CAT_IN_DAT': '',
    'UTM_ZONE': 'verbatimCoordinateSystem',
    'UTM_EAST': 'verbatimLongitude',
    'UTM_NORTH': 'verbatimLatitude',
    'ANALYSIS': 'preparations',
    'FORMATION': 'formation',
    'OLD SAMPLE NO': 'recordNumber'
}
df.rename(columns=mapping, inplace=True)

df['eventDate'] = df['verbatimEventDate']
date_fixes = ['-00-00', '-00', '00/00/', '00/', '00.00', '00.', '?', ' ']
for date_fix in date_fixes:
    df['eventDate'] = df['eventDate'].str.replace(date_fix, '')
df.loc[df['eventDate'] == '0', 'eventDate'] = ''
df = df.fillna('')
date_fixes = {'`': '19', '': }

def parse_dates(date):
    try:
        new = parser.parse(date, )
        if pd.isnull(new):
            return ''

        if len(date) ==
        return new
    except Exception as e:
        #print(e)
        #print(date)
        return ''

df['eventDate'] = df['eventDate'].apply(parse_dates)
df['modified'] = df['modified'].apply(parse_dates)
df = df.fillna(' ')  # see https://github.com/pandas-dev/pandas/issues/11953

def convert_utm(row):
    if  row['verbatimLatitude'] == '' or row['verbatimLatitude'] == '0' \
        or row['verbatimLongitude'] == '' or row['verbatimLongitude'] == '0' \
        or row['verbatimCoordinateSystem'] == '' or row['verbatimCoordinateSystem'] == '0' \
        or len(row['verbatimCoordinateSystem']) != 3:
        return ('', '')
    try:
        zone_letter = row['verbatimCoordinateSystem'][-1]
        zone = int(row['verbatimCoordinateSystem'][:-1])
        utmlat = int(row['verbatimLatitude'])
        utmlong = int(row['verbatimLongitude'])
        lat, long = utm.to_latlon(utmlong, utmlat, zone, zone_letter)
        return (lat, long)
    except Exception as e:
        import pdb; pdb.set_trace()

df['decimalDegrees'] = df.apply(convert_utm, axis=1)
df['decimalLatitude'] = df['decimalDegrees'].str[0]
df['decimalLongitude'] = df['decimalDegrees'].str[1]

df['catalogNumber'] = 'NHMO-MU-' + df['catalogNumber'].str.rstrip(', ')

df.to_csv('occurrence.csv', sep='\t')

#%%
import pandas as pd
from dateutil import parser
import utm
#%%
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

class MyParserInfo(parser.parserinfo):
    MONTHS = [('Jan', 'January', 'januar'), 
            ('Feb', 'February', 'februar'),
            ('Mar', 'March', 'mars'),
            ('Apr', 'April', 'april'),
            ('May', 'May', 'mai'),
            ('Jun', 'June', 'juni'),
            ('Jul', 'July', 'juli'),
            ('Aug', 'August'),
            ('Sep', 'Sept', 'September'),
            ('Oct', 'October', 'oktober'),
            ('Nov', 'November'),
            ('Dec', 'December')]

def get_date_string(date):
    if date is None or date == 0 or date == '0' or pd.isnull(date) or 'ukjent' in date.lower():
        return None
    date_fixes = [' - 1874-1879', 'xx/', 'xx/yy', '-00-00', '-00', '00/00/', '00/', '00.00', '00.', '?', ' ', '00:00:00', 'Summer', 'Sommeren', ',Oslo', 'Benecke', 'Vorrended.', 'J.Lehmann', 'Rosenbusch', ' - 1914-1915', ' - 1876-1877', ' - 1874-1879', ' - 1911-1912', 'HoelsSpitsbergeneksp.']
    for date_fix in date_fixes:
        date = date.replace(date_fix, '')
    date = date.replace('`', '19')
    date = date.strip(' .-/|')

    try:
        norwegian_months = ['januar', 'februar', 'mars', 'april', 'mai', 'juni', 'juli', 'oktober', 'feby']
        for month in norwegian_months:
           date = date.replace(month, month[:3]).replace('mai', 'may').replace('okt', 'oct')
        period = pd.Period(date)
        format = '%Y-%m-%d'
        if period.freqstr == 'M':
            format = '%Y-%m'
        elif period.freqstr == 'A-DEC':
            format = '%Y'
        return period.strftime(format)
    except pd._libs.tslibs.parsing.DateParseError as e:
        try:
            output = parser.parse(date, dayfirst=True, parserinfo=MyParserInfo())
            return output.strftime('%Y-%m-%d')
        except parser._parser.ParserError as e:
            print(f'{e} - {date}')
            return ''
    except Exception as e:
        print(f'{e} - {date}')
        #import pdb; pdb.set_trace()
        return ''

df['eventDate'] = df['verbatimEventDate'].apply(get_date_string)
df['modified'] = df['modified'].apply(get_date_string)
#df = df.fillna(' ')  # see https://github.com/pandas-dev/pandas/issues/11953

def convert_utm(row):
    if  row['verbatimLatitude'] == '' or row['verbatimLatitude'] == '0' \
        or row['verbatimLongitude'] == '' or row['verbatimLongitude'] == '0' \
        or row['verbatimCoordinateSystem'] == '' or row['verbatimCoordinateSystem'] == '0' \
        or pd.isnull(row['verbatimLatitude']) or pd.isnull(row['verbatimLongitude']) or pd.isnull(row['verbatimCoordinateSystem']) \
        or len(row['verbatimCoordinateSystem']) != 3:
        return ('', '')
    try:
        zone_letter = row['verbatimCoordinateSystem'][-1]
        zone = int(row['verbatimCoordinateSystem'][:-1])
        utmlat = int(row['verbatimLatitude'])
        utmlong = int(row['verbatimLongitude'])
        lat, long = utm.to_latlon(utmlong, utmlat, zone, zone_letter)
        return (round(lat, 3), round(long, 3))
    except Exception as e:
        return (None, None)

df['decimalDegrees'] = df.apply(convert_utm, axis=1)
df['decimalLatitude'] = df['decimalDegrees'].str[0]
df['decimalLongitude'] = df['decimalDegrees'].str[1]

df['catalogNumber'] = 'NHMO-MU-' + df['catalogNumber'].str.rstrip(', ')
df.to_csv('occurrence.txt', sep='\t', index=False)
import pdb; pdb.set_trace()

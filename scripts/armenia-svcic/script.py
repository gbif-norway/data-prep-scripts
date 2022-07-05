import pandas as pd
from uuid import uuid4

data = pd.read_csv('from-alvina-corrected.csv', dtype='str')

# Column mapping/dropping
mapping = {
    'PUID': 'occurrenceID',
    'INSTCODE': 'institutionCode',
    'ACCENUMB': 'catalogNumber',
    'COLLNUMB': 'recordNumber',
    'GENUS': 'genus',
    'SPECIES': 'specificEpithet',
    'SPAUTHOR': 'scientificNameAuthorship',
    'SUBTAXA': 'infraSpecificEpithet',
    'CROPNAME': 'vernacularName',
    'ACCENAME': 'cultivarEpithet',
    'ACQDATE': 'acquisitionDate',
    'ORIGCTY': 'countryCode',
    'COLLSITE': 'locality',
    'COLLDATE': 'eventDate',
    'BREDCODE': 'breedingInstituteID',
    'SAMPSTAT': 'biologicalStatus',
    'ANCEST': 'ancestralData',
    'COLLSRC': 'acquisitionSource',
    'DONORCODE': 'donorInstituteID',
    'DONORNUMB': 'donorsIdentifier',
    'OTHERNUMB': 'otherCatalogNumbers',
    'DUPLSITE': 'safetyDuplicationInstituteID',
    'STORAGE': 'storageCondition',
    'MLSSTAT': 'mlsStatus'
}
data.drop(columns=[col for col in data if col not in mapping.keys()], inplace=True)
data.rename(columns=mapping, inplace=True)

# Fix date formats
date_columns = ['acquisitionDate', 'eventDate']
for date_column in date_columns:
    data[date_column] = data[date_column].str.replace('-', '')
    data[date_column] = data[date_column].str.replace(r'^(\d\d\d\d)(\d\d)(\d\d)$', r'\1-\2-\3')
    data[date_column] = data[date_column].str.replace(r'^(\d\d\d\d)(\d\d)$', r'\1-\2')

# Add basisOfRecord and uuids for missing occurrenceIDs
data['basisOfRecord'] = 'occurrence'
data.loc[data['occurrenceID'].isna(), 'occurrenceID'] = [uuid4() for x in range(data['occurrenceID'].isna().sum())]

# Output
data.to_csv('converted.csv', index=False)
import pdb; pdb.set_trace()

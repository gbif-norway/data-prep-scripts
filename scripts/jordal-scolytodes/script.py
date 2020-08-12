import pandas as pd
import numpy as np
import uuid

col_mapping = {'ScientificNameAuthor': 'scientificNameAuthorship', 'doi:': 'namePublishedInID', 'ScientificName': 'scientificName', 'Collector': 'recordedBy'}
event_col_mapping = {'MinElevation': 'minimumElevationInMeters', 'MaxElevation': 'maximumElevationInMeters', 'Latitude': 'decimalLatitude', 'Longitude': 'decimalLongitude', 'DateCollected': 'eventDate', 'Notes': 'samplingProtocol', 'Province': 'stateProvince', 'Country': 'country', 'Locality': 'locality'}
new_species = ['']
orcids = {
        'Bjarte Henry Jordal': 'https://orcid.org/0000-0001-6082-443X',
        'Lawrence Kirkendall': 'https://orcid.org/0000-0002-7335-6441',
        'Sarah M. Smith': 'https://orcid.org/0000-0002-5173-3736'
}
collector_orcids = {
        'Kirkendall': 'https://orcid.org/0000-0002-7335-6441',
        'Storer': 'https://orcid.org/0000-0002-0349-0653',
        'Johnson': 'https://orcid.org/0000-0003-3139-2257',
        'Anderson': 'https://orcid.org/0000-0003-0665-2977',
        'Atkinson': 'https://orcid.org/0000-0002-9675-8507',
        'Osborn': 'https://orcid.org/0000-0002-4059-4435',
        'Erwin': 'https://orcid.org/0000-0002-9510-3197',
        'Hulcr': 'https://orcid.org/0000-0002-8706-4618'
}

files_and_author = {'2020': 'Jordal and Smith, 2020', '2019': 'Jordal & Kirkendall', '2018': 'Jordal, 2018'}
for file_name, author in files_and_author.items():
    print('working on ' + file_name)
    # Load the main file and the lsids for the specimens (extracted using regex from the PDF publications)
    main = pd.read_excel(file_name + '.xls', 'main', dtype='str')
    main = main.fillna('')

    # UUIDs and basis of record
    main['occurrenceID'] = [uuid.uuid4() for x in range(len(main.index))]
    main['basisOfRecord'] = 'PreservedSpecimen'

    # Dwcify cols
    main.rename(columns=col_mapping, inplace=True)
    main.rename(columns=event_col_mapping, inplace=True)

    # Create events based on event_col_mapping
    events = main[list(event_col_mapping.values())].copy()
    events.drop_duplicates(inplace=True)
    events['eventID'] = [uuid.uuid4() for x in range(len(events.index))]
    # Note that there are some events in the same location, same date, same collector but a different sampling protocol
    main['eventID'] = main.merge(events, how='left', on=list(event_col_mapping.values()))['eventID']
    main.drop(event_col_mapping.values(), axis=1, inplace=True)

    # Add orcids and ID info
    main['identifiedBy'] = 'Bjarte Henry Jordal'
    main['identifiedByID'] = orcids['Bjarte Henry Jordal']
    main['recordedByID'] = ''
    for surname, orcid in collector_orcids.items():
        main.loc[main['recordedBy'].str.contains(surname), 'recordedByID'] = orcid

    # Add type info - looks like it isn't possible to do this as there is no way to link individual occurrences to lsids and typestatuses
    #main['typeStatus'] = ''
    #import pdb; pdb.set_trace()
    #main.loc[main['scientificNameAuthorship'] == author and ~main.duplicated(subset=['scientificName']), 'typeStatus'] = 'holotype of ' + main['scientificName'] + '. ' + main['namePublishedInID']
    #lsids = pd.read_json(file_name + '-lsids.json', orient='values')
    #main.loc[(~main.duplicated(subset=['scientificName'])) & main['scientificNameAuthorship'] == author]
    #lsids.columns = ['scientificName', 'scientificNameID']
    #main = main.merge(lsids, how='left', on='scientificName')

    main.to_csv(file_name + '_occurrences.csv', index=False, date_format='%Y-%m-%d')
    events.to_csv(file_name + '_events.csv', index=False, date_format='%Y-%m-%d')

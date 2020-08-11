import pandas as pd
import numpy as np
import uuid

col_mapping = {'ScientificNameAuthor': 'scientificNameAuthorship', 'doi:': 'namePublishedInID'}
event_col_mapping = {'MinElevation': 'minimumElevationInMeters', 'MaxElevation': 'maximumElevationInMeters', 'Latitude': 'decimalLatitude', 'Longitude': 'decimalLongitude', 'Collector': 'recordedBy', 'DateCollected': 'eventDate', 'Notes': 'samplingProtocol', 'Province': 'stateProvince', 'Country': 'country', 'Locality': 'locality'}
new_species = ['']
orcids = {
        'Bjarte Henry Jordal': 'https://orcid.org/0000-0001-6082-443X',
        'Lawrence Kirkendall': 'https://orcid.org/0000-0002-7335-6441',
        'Sarah M. Smith': 'https://orcid.org/0000-0002-5173-3736'
}

# Main
for file_name in ['Scolytodes 2020.xls', 'Scolytodes 2019.xls', 'Scolytodes 2018.xls']:
    main = pd.read_excel(file_name, 'main', dtype='str')
    main['occurrenceID'] = [uuid.uuid4() for x in range(len(main.index))]
    main.rename(columns=col_mapping, inplace=True)
    main.rename(columns=event_col_mapping, inplace=True)
    main['identifiedBy'] = 'Bjarte Henry Jordal'
    main['identifiedByID'] = orcids['Bjarte Henry Jordal']

    # Create events based on event_col_mapping
    events = main[list(event_col_mapping.values())].copy()
    events.drop_duplicates(inplace=True)
    events['eventID'] = [uuid.uuid4() for x in range(len(events.index))]
    # Note that there are some events in the same location, same date, same collector but a different sampling protocol

    main['eventID'] = main.merge(events, how='left', on=list(event_col_mapping.values()))['eventID']
    main.drop(event_col_mapping.values(), axis=1, inplace=True)

    # Link
    import pdb; pdb.set_trace()


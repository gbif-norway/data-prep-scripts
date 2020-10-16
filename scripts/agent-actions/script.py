import pandas as pd
from zipfile import ZipFile, BadZipFile
import os.path
import helpers

dwc_file = '/srv/scripts/agent-actions/dwc.zip'
if not os.path.isfile(dwc_file):
    helpers.store_dwca('https://ipt.gbif.no/archive.do?r=trom_lichens', dwc_file)

with ZipFile(dwc_file) as zf:
    with zf.open('occurrence.txt') as core:
        df = pd.read_csv(core, sep='\t', dtype='str')
        df_orig = df.copy()

        collector_columns = ['year', 'month', 'day', 'recordedBy']
        collector_df = helpers.create_collector_agents(df[collector_columns + ['occurrenceID']].copy())
        df.drop(collector_columns, axis=1, inplace=True)

        identifier_columns = ['identifiedBy', 'dateIdentified', 'occurrenceID']
        identifier_df = pd.concat([df[col] for col in identifier_columns], axis=1, keys=['name', 'startedAtTime', 'occurrenceID'])
        identifier_df['action'] = 'identified'
        identifier_df['role'] = 'identifier?'

        agents = pd.concat([collector_df, identifier_df])
        import pdb; pdb.set_trace()
        agents['type'] = 'http://schema.org/Person'
        print(agents)

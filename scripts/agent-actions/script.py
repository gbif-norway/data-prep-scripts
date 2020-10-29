import pandas as pd
from zipfile import ZipFile, BadZipFile
import os.path
import helpers

dwc_file = '/srv/scripts/agent-actions/dwc.zip'
if not os.path.isfile(dwc_file):
    helpers.store_dwca('https://ipt.gbif.no/archive.do?r=o_vascular', dwc_file)

agent_qids = pd.read_csv('vascular-plant-collectors.csv', dtype='str')
agent_qids['name'] = agent_qids['name'].str.replace(r'\s+\(.+', '')

with ZipFile(dwc_file) as zf:
    with zf.open('occurrence.txt') as core:
        df = pd.read_csv(core, sep='\t', dtype='str', error_bad_lines=False)
        df_orig = df.copy()

        collector_columns = ['year', 'month', 'day', 'recordedBy']
        collector_df = helpers.create_collector_agents(df[collector_columns + ['occurrenceID']].copy())
        collector_df = collector_df.merge(agent_qids, how='left', on=['name'])
        df.drop(collector_columns, axis=1, inplace=True)

        identifier_columns = ['identifiedBy', 'dateIdentified']
        identifier_df = helpers.create_identifier_agents(df[identifier_columns + ['occurrenceID']].copy())
        identifier_df = identifier_df.merge(agent_qids, how='left', on=['name'])
        df.drop(identifier_columns, axis=1, inplace=True)

        agents = pd.concat([collector_df, identifier_df])
        agents['agentIdentifierType'] = 'Wikidata'
        agents['identifier'] = 'https://www.wikidata.org/wiki/' + agents['identifier']
        agents['type'] = 'http://schema.org/Person'

        agents[pd.notnull(agents['identifier'])].to_csv('agents.csv', index=False)
        df.to_csv('occurrence.csv', index=False)
        import pdb; pdb.set_trace()


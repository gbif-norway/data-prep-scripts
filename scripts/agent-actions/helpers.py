import requests
import pandas as pd

def store_dwca(url, result_file):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(result_file, 'wb') as fd:
        for chunk in response.iter_content(5000):
            fd.write(chunk)

def make_date(year, month, day):
    date = year + '-' + month + '-' + day
    return date.str.strip('-').str.strip('-')

def stack_agents(df):
    # Split collector by ',' delimiter, and stack them one on top of the other to make one dataframe
    df = df.set_index(['occurrenceID', 'startedAtTime'])['name'].str.split(',', expand=True).stack().reset_index(['occurrenceID', 'startedAtTime'])
    return df.rename(columns={0: 'name'})

def create_identifier_agents(df):
    # Make temporary dataframe with correct columns and get agents
    df_temp = pd.concat([df['identifiedBy'], df['dateIdentified'], df['occurrenceID']], axis=1, keys=['name', 'startedAtTime', 'occurrenceID'])
    df = stack_agents(df_temp)

    # Strip name, add action and return
    df['name'] = df['name'].str.strip()
    df['action'] = 'identified'
    return df

def create_collector_agents(df):
    # Create date
    df['eventDate'] = make_date(df['year'], df['month'],  df['day'])

    # Make temporary dataframe with correct columns and get agents
    df_temp = pd.concat([df['recordedBy'], df['eventDate'], df['occurrenceID']], axis=1, keys=['name', 'startedAtTime', 'occurrenceID'])
    df = stack_agents(df_temp)

    # Add default action and role info
    df['action'] = 'collected'
    df['role'] = 'primary collector role'  # http://purl.obolibrary.org/obo/CRO_0000094

    # Some collectors are secondary collectors, I think it is fairly safe to rely on the ", " delimiter, which means
    # all collectors beginning with ' ' are secondary
    df.loc[df['name'].str[0] == ' ', 'role'] = 'specimen collection role'
    df['name'] = df['name'].str.strip()

    return df


#%%
import pandas as pd
import requests
#%%
df = pd.read_csv('input.csv', dtype='str')
#%%
def extract(occid):
    r = requests.get(url = f'https://api.gbif.org/v1/occurrence/search?occurrenceID={occid}')
    data = r.json()
    key, locality, event_date = '[None]', '[None]', '[None]' 
    if data['count'] == 1:
        res = data['results'][0]
        key = res['key']
        locality = '[None]' if 'locality' not in res else res['locality']
        event_date = '[None]' if 'eventDate' not in res else res['eventDate']
    return key, locality, event_date
#%%
df['occurrenceKey'], df['locality'], df['eventDate.1'] = zip(*df['occurenceID'].map(extract))
# %%
df.to_csv('output.csv', index=False)
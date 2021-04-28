import requests
import pandas as pd

GBIF = 'https://api.gbif.org/v1/{}'
response = requests.get(GBIF.format('dataset?type=OCCURRENCE&country=NO&limit=1000'))
all_datasets = response.json()['results']
collections = []
for ds in all_datasets:
    response = requests.get(GBIF.format('dataset/{}', ds['key']))
    ipt = response.json()['identifiers'][0]['identifier']
    FACET_SEARCH = GBIF.format('occurrence/search?datasetKey={}&facet={}&limit=0')
    response = requests.get(FACET_SEARCH.format(ds['key'], 'institutionCode'))
    institution_codes = [r['name'] for r in response.json()['facets'][0]['counts']]
    response = requests.get(FACET_SEARCH.format(ds['key'], 'collectionCode'))
    collection_codes = [r['name'] for r in response.json()['facets'][0]['counts']]
    collections.append({
        'key': ds['key'],
        'ipt': ipt,
        'title': ds['title'],
        'keywords': '|'.join(ds['keywords']),
        'publishingOrganizationKey': ds['publishingOrganizationKey'],
        'installationKey': ds['installationKey'],
        'institution_codes': '|'.join(institution_codes),
        'collection_codes': '|'.join(collection_codes)
        })

collections_df = pd.DataFrame(collections)

response = requests.get(GBIF.format('grscicoll/collection?country=NO'))
all_grscicoll = response.json()['results']
grscicoll = []
for cs in all_grscicoll:
    grscicoll.append({
        'institutionCode': cs['institutionCode'],
        'institutionName': cs['institutionName'],
        'collectionCode': cs['code'],
        'key': cs['key'],
        'institutionKey': cs['institutionKey']})
grscicoll_df = pd.DataFrame(grscicoll)

import pdb; pdb.set_trace()

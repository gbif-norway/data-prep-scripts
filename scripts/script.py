#%%
import pandas as pd
import uuid
#%%
pivot = pd.read_excel('https://zenodo.org/record/7588934/files/solhomfjell.xlsx?download=1')
#%%
pivot['locationCode'] = pivot['Repeat'].astype(str) + '_' + pivot['Route'].astype(str)
pivot.drop(['Repeat', 'Route', 'Subset'], axis=1, inplace=True)
pivot = pivot.iloc[:, :-5]
#%%
pivot['eventID'] = pivot.apply(lambda x: uuid.uuid4(), axis=1)
pivot['locationID'] = pivot.apply(lambda x: uuid.uuid4(), axis=1)
pivot
# %%
events = pivot[['eventID', 'locationID', 'locationCode']]
events
#%%
occs = pd.melt(pivot, id_vars=['locationCode', 'eventID', 'locationID'], var_name='scientificName', value_name='subplotCount')
occs['occurrenceID'] = occs.apply(lambda x: uuid.uuid4(), axis=1)
#%%
occs['occurrenceStatus'] = occs['subplotCount'].apply(lambda x: 'present' if x > 0 else 'absent')
#occs['organismQuantity'] = occs['individualCount']
#occs['organismQuantityType'] = 'subplot frequency of 16'
occs['recordedByID'] = 'https://orcid.org/0000-0002-6859-7726'
occs['institutionID'] = 'https://ror.org/01xtthb56'
occs['basisOfRecord'] = 'humanobservation'
occs
#%%
events.to_csv('events.csv', index=False)
occs.to_csv('occurrences.csv', index=False)
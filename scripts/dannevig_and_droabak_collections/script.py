#%%
import pandas as pd
from dateutil import parser
# %%
data_e_dan = pd.read_csv('event_dan.csv', sep='\t')
data_e_dro = pd.read_csv('event_dro.csv', sep='\t')
# %%
data_e = pd.concat([data_e_dan, data_e_dro])

# %%
data_o = pd.read_csv('occurrence_orig.csv', sep='\t')
# %%
data_e_c = data_e[['locationID', 'eventID']]
# %%
res = pd.merge(data_e_c, data_o, how='right', left_on='locationID', right_on='locationRemarks')
# %%
res = res[res.columns.drop('locationID')]
res.modified = res.modified.apply(parser.parse)
# %%
res.to_csv('occurrence.csv', sep='\t')
# %%
data_e.to_csv('event.csv', sep='\t')
# %%

# %%

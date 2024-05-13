#%%
import pandas as pd
from uuid import uuid4
import re
# %%
orig = pd.read_excel('/srv/scripts/sav/orig/dwc.xls', sheet_name=None)
# %%
orig
# %%
data = []
for key, val in orig.items():
    val.columns=['id', 'specificEpithet', 'locality', 'catalogNumber', 'decimalLatitude',
       'decimalLongitude']
    val['scientificName'] = key
    data.append(val)
# %%
merged = pd.concat(data)
# %
merged['catalogNumber'] = merged['catalogNumber'].apply(lambda x: [y.strip() for y in x.split(',')])
# %%
merged = merged.explode('catalogNumber')
# %%
def extract_leading_letters(string):
    # Compile the regular expression to match leading letters
    pattern = re.compile(r'^[A-Za-z]+')
    # Attempt to match the pattern at the start of the string
    match = pattern.match(string)
    # Return the matched group if a match is found, otherwise return None
    return match.group() if match else None
# %%
merged['institutionCode'] = merged['catalogNumber'].apply(extract_leading_letters)
# %%
merged['occurrenceID'] = merged.apply(lambda _: uuid4(),axis=1)
# %%
merged.to_excel('/srv/scripts/sav/res.xlsx', index=False)
# %%

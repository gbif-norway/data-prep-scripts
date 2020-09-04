import pandas as pd
import numpy as np
import uuid
import re
from helpers import split_rows

# POND BED SOUTH (PBS)
raw = pd.read_excel('Bed5_PBS.xlsx', 'Sheet1', usecols=['scientificname', 'vernacularname', 'vernacularname-no', 'bed', 'comments'], dtype='str')
raw['occurrenceid'] = [uuid.uuid4() for x in range(len(raw.index))]

new_df = []
for index, row in raw.iterrows():
    new_df.extend(split_rows(row['comments'], row['occurrenceid']))
exploded = pd.DataFrame(new_df)
exploded['type'] = 'Stillimage'
exploded['format'] = 'image/jpeg'
exploded['identifier'] = 'https://static.gbif.no/ipt-specimens/[dataset-id]/' + exploded['file_name'] + '.jpg'

del raw['comments']
raw.to_csv('occurrence.csv', index=False)
exploded.to_csv('multimedia.csv', index=False)

import pandas as pd
import numpy as np
import uuid
import re
from helpers import split_rows, merge_duplicate_taxa

# POND BED SOUTH (PBS)
raw = pd.read_excel('Bed5_PBS.xlsx', 'Sheet1', usecols=['scientificname', 'vernacularname', 'vernacularname-no', 'bed', 'comments'], dtype='str')
merged = merge_duplicate_taxa(raw)
merged['taxonid'] = [uuid.uuid4() for x in range(len(merged.index))]

images = []
for index, row in merged.iterrows():
    images.extend(split_rows(row['comments'], row['taxonid']))
images = pd.DataFrame(images)
images['type'] = 'Stillimage'
images['format'] = 'image/jpeg'
images['identifier'] = 'https://static.gbif.no/ipt-specimens/[dataset-id]/' + images['file_name'] + '.jpg'
images['creator'] = 'Stephen Barstow'
images.to_csv('multimedia.csv', index=False)

occurrences = images[['created', 'taxonid']].drop_duplicates()
occurrences['occurrenceid'] = [uuid.uuid4() for x in range(len(occurrences.index))]

occurrence_df = occurrences[['occurrenceid', 'taxonid']]
occurrence_df['recordedBy'] = 'Stephen Barstow'
occurrence_df['decimalLatitude'] = '63.434'
occurrence_df['decimalLongitude'] = '10.671'
occurrence_df['coordinateUncertaintyInMeters'] = '5000'
occurrence_df['establishmentMeans'] = 'managed'
occurrence_df['basisOfRecord'] = 'humanobservation'
occurrence_df.to_csv('occurrence.csv', index=False)

merged[['scientificname', 'taxonid']].to_csv('taxon.csv', index=False)

vn_en = merged[['vernacularname', 'taxonid']]
vn_en = vn_en.assign(vernacularname=vn_en['vernacularname'].str.split('[,|;]')).explode('vernacularname')
vn_en['language'] = 'EN'
vn_no = merged[['vernacularname-no', 'taxonid']]
vn_no.rename(columns={'vernacularname-no': 'vernacularname'}, inplace=True)
vn_no = vn_no.assign(vernacularname=vn_no['vernacularname'].str.split('[,|;]')).explode('vernacularname')
vn_no['language'] = 'NB'
vern = pd.concat([vn_en, vn_no])
vern = pd.concat([vn_en, vn_no]).dropna()
vern['vernacularname'] = vern['vernacularname'].str.strip()
vern.to_csv('vernacularname.csv', index=False)


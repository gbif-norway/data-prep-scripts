import pandas as pd
import numpy as np
import uuid
import re
from helpers import split_rows, merge_duplicate_taxa, get_date
from os import listdir
import shutil

# POND BED SOUTH (PBS)
# This spreadsheet has one row per scientific name
# Images are concatenated in row E
# There is a very complicated naming system for the image files, and the date of observation is in brackets for the most part after each image file
raw = pd.read_excel('Bed5_PBS.xlsx', 'Sheet1', usecols=['scientificname', 'vernacularname', 'vernacularname-no', 'bed', 'comments'], dtype='str')

# There SHOULD be one row per scientific name, but sometimes there isn't, so fix that and assign an ID
merged = merge_duplicate_taxa(raw)
merged['taxonid'] = [uuid.uuid4() for x in range(len(merged.index))]

# helpers.py contains the split_rows function which splits into one row per image
images = []
for index, row in merged.iterrows():
    images.extend(split_rows(row['comments'], row['taxonid']))
images = pd.DataFrame(images)
images['type'] = 'Stillimage'
images['format'] = 'image/jpeg'
images['creator'] = 'Stephen Barstow'

# Files in directory
file_names_list = [file_name.split('.')[0] for file_name in listdir('imgs/')]
file_names_split = pd.Series(file_names_list).str.extract('(?P<camera>[^\d]+)(?P<file_number>\d+)')

# Files in dataframe
files_df = images['file_name'].str.extract('(?P<camera>[^\d]+)(?P<file_number>\d+)')
images = images.merge(files_df, left_index=True, right_index=True)

# Join IMG_ files normally, treat P files separately further down
images['file_exists_img'] = images['file_name'].isin(file_names_list)
# Doesn't seem to be any of these, but there might be in the future so let's leave it in

# Get dates info into separate cols
images['created_month'] = images['created'].str[2:4]
images['created_day'] = images['created'].str[0:2]
images['created_year'] = images['created'].str[4:6]

# Construct a sensible date
images['created'] = get_date(images['created_year'], images['created_month'], images['created_day'])

# For file names, month needs to be A, B, C for 10, 11 and 12
images.loc[images['created_month'] == '10', 'created_month'] = 'A'
images.loc[images['created_month'] == '11', 'created_month'] = 'B'
images.loc[images['created_month'] == '12', 'created_month'] = 'C'
images['created_month'] = images['created_month'].str.strip('0')

# More complicated cases for P files
images['real_file_name'] = images['camera'] + images['created_month'] + images['created_day'] + images['file_number'].str[-4:]
# subset = images[images['file_name'].str[0] == 'P']
# temp = subset.pivot_table(values='camera', aggfunc='count', index=['created_year','file_name'])
# last thing i was trying to look at - are there actually duplicate file names in here?
images['exists'] = images['real_file_name'].isin(file_names_list)

# print(len(images[images['exists'] == True]))
used_images = images.loc[images['exists'] == True]
#for image in used_images['real_file_name'].to_list():
#    shutil.copy('imgs/' + image + '.JPG', 'used_imgs/' + image + '.jpg')
used_images['identifier'] = 'https://static.gbif.no/ipt-specimens/barstow-garden/' + images['created_year'] + '/' + images['real_file_name'] + '.jpg'

# We can note one occurrence per group of images (group of images all taken on a certain date)
occurrences = images[['created', 'taxonid']].drop_duplicates()
occurrences['occurrenceid'] = [uuid.uuid4() for x in range(len(occurrences.index))]

# Create multimedia.csv
used_images.merge(occurrences, how='left', on=['created', 'taxonid']).to_csv('multimedia.csv', index=False)

# Create occurrence.csv
occurrences['recordedBy'] = 'Stephen Barstow'
occurrences['decimalLatitude'] = '63.434'
occurrences['decimalLongitude'] = '10.671'
occurrences['coordinateUncertaintyInMeters'] = '5000'
occurrences['establishmentMeans'] = 'managed'
occurrences['basisOfRecord'] = 'humanobservation'
occurrences.merge(merged, how='left', on='taxonid').to_csv('occurrence.csv', index=False)

# In case one wishes to publish as checklist
# merged[['scientificname', 'taxonid']].to_csv('taxon.csv', index=False)

# Attempt to do vernacular names, but I think this is beyond scope
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
vern[vern['vernacularname'] != ''].to_csv('vernacularname.csv', index=False)


import pandas as pd
import numpy as np
import uuid
import re
from helpers import split_rows, merge_duplicate_taxa, get_date
from os import listdir
import shutil

for source_file in ['Bed5_PBS']:
    # These spreadsheet have one row per scientific name
    # Images are concatenated in row E
    # There is a very complicated naming system for the image files, and the date of observation is in brackets for the most part after each image file
    raw = pd.read_excel(source_file + '.xlsx', 'Sheet1', usecols=['scientificname', 'vernacularname', 'vernacularname-no', 'bed', 'comments'], dtype='str')

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

    # Files in directories
    file_names_list = []
    for img_dir in listdir('imgs/'):
        #file_names_list = [file_name.split('.')[0] for file_name in listdir('imgs/{}/'.format(img_dir))]
        # file_names_split = pd.Series(file_names_list).str.extract('(?P<camera>[^\d]+)(?P<file_number>\d+)')
        file_names_list += ['{}/{}'.format(img_dir, fname.split('.')[0]) for fname in listdir('imgs/{}/'.format(img_dir))]

    # Files in dataframe
    files_df = images['file_name'].str.extract('(?P<camera>[^\d]+)(?P<file_number>\d+)')
    files_df['file_number']  = files_df['file_number'].astype(str)
    images = images.merge(files_df, left_index=True, right_index=True)

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

    # Join IMG_ files normally, treat P files separately further down
    # images['file_exists_img'] = images['created_year'] + '/' + images['file_name']
    # images['file_exists_img'] = images['file_exists_img'].isin(file_names_list)
    # Doesn't seem to be any of these, but there might be in the future so let's leave it in

    # More complicated cases for P files
    images['real_file_name'] = images['camera'] + images['created_month'] + images['created_day'] + images['file_number'].str[-4:]

    # IMG files need to be 0 padded to 4 chars
    images.loc[(images['camera'] == 'IM') & (images['file_number'].str.len() < 4), 'file_number'] = '0' + images.loc[(images['camera'] == 'IM') & (images['file_number'].str.len() < 4), 'file_number']
    images.loc[images['camera'] == 'IM', 'real_file_name'] = 'IMG_' + images.loc[images['camera'] == 'IM', 'file_number']

    # HP files also need to be changed
    images.loc[images['camera'] == 'HP', 'real_file_name'] = 'HPIM' + images.loc[images['camera'] == 'HP', 'file_number']

    images['real_file_name'] = '20' + images['created_year'] + '/' + images['real_file_name']
    images['exists'] = images['real_file_name'].isin(file_names_list)

    # print(len(images[images['exists'] == True]))
    used_images = images.loc[images['exists'] == True]
    for image in used_images['real_file_name'].to_list():
        shutil.copy('imgs/' + image + '.JPG', 'used_imgs/' + image + '.jpg')
    used_images['identifier'] = 'https://static.gbif.no/ipt-specimens/barstow-garden/' + images['real_file_name'] + '.jpg'
    import pdb; pdb.set_trace()

    # We can note one occurrence per group of images (group of images all taken on a certain date)
    occurrences = images[['created', 'taxonid']].drop_duplicates()
    occurrences['occurrenceid'] = [uuid.uuid4() for x in range(len(occurrences.index))]

    # Create multimedia.csv
    used_images.merge(occurrences, how='left', on=['created', 'taxonid']).to_csv(source_file + '__multimedia.csv', index=False)

    # Create occurrence.csv
    occurrences['recordedBy'] = 'Stephen Barstow'
    occurrences['decimalLatitude'] = '63.434'
    occurrences['decimalLongitude'] = '10.671'
    occurrences['coordinateUncertaintyInMeters'] = '5000'
    occurrences['establishmentMeans'] = 'managed'
    occurrences['basisOfRecord'] = 'humanobservation'
    occurrences['eventDate'] = occurrences['created']
    occurrences.rename(inplace=True, columns={'created': 'eventDate', 'bed': 'eventRemarks'})
    occurrences.merge(merged, how='left', on='taxonid').to_csv(source_file + '__occurrence.csv', index=False)

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
    vern[vern['vernacularname'] != ''].to_csv(source_file + '__vernacularname.csv', index=False)


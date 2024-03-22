import pandas as pd

mapping = pd.read_csv('mapping-museum-numbers.csv', dtype=str)
mapping[['old_collection_code', 'old_catalog_number']] = mapping['OLD_IDENTIFIER_STRING'].str.extract(r'([A-Za-z]+)-?(\d+)')
lep = pd.read_csv('o_lepidoptera.txt', dtype=str, sep='\t', usecols=['id', 'collectionCode', 'catalogNumber', 'recordedBy', 'scientificName']) 
mapped_lep = pd.merge(mapping, lep, left_on='IDENTIFIER_NUM', right_on='catalogNumber', how='left')
missing_in_lep = mapping[~mapping['IDENTIFIER_NUM'].isin(lep['catalogNumber'])]

het = pd.read_csv('o_het.txt', dtype=str, sep='\t', usecols=['collectionCode', 'catalogNumber', 'recordedBy', 'scientificName'])
hym = pd.read_csv('o_hym.txt', dtype=str, sep='\t', usecols=['collectionCode', 'catalogNumber', 'recordedBy', 'scientificName'])
div = pd.read_csv('o_div.txt', dtype=str, sep='\t', usecols=['collectionCode', 'catalogNumber', 'recordedBy', 'scientificName'])
dip = pd.read_csv('o_dip.txt', dtype=str, sep='\t', usecols=['collectionCode', 'catalogNumber', 'recordedBy', 'scientificName'])

het['source'] = het.collectionCode.unique()[0]
het['original_dataset_id'] = '1acdfdd0-e43d-4d5d-92bc-7a2a60a03782'
hym['source'] = hym.collectionCode.unique()[0]
hym['original_dataset_id'] = 'a4e7ff0a-f9c0-481a-88ed-5986ec86b24a'
div['source'] = div.collectionCode.unique()[0]
div['original_dataset_id'] = '4cfd80a7-d630-4d7f-89fb-d2d1e749a418'
dip['source'] = dip.collectionCode.unique()[0]
dip['original_dataset_id'] = 'bb39604c-3731-49ce-a9dc-f3617d3d0d15'
old = pd.concat([het, hym, div, dip], ignore_index=True)

old_joined_to_new = pd.merge(old, mapped_lep, left_on=['catalogNumber', 'scientificName'], right_on=['old_catalog_number', 'scientificName'], how='left', indicator=True, suffixes=['_old', '_mapped_lep'])

# We get some perfect matches
matched_records = old_joined_to_new[old_joined_to_new['_merge'] == 'both']
matched_records['original_occ_id'] = 'urn:catalog:O:' + matched_records['source'] + ':' + matched_records['catalogNumber_old'].astype(str)
matched_records['new_occ_id'] = matched_records['id']
matched_records['original_dataset'] = matched_records['source']
matches_on_sn = matched_records[['original_occ_id', 'new_occ_id', 'original_dataset_id']]

# From the unmatched, search just based on catalogNumber without scientificName
no_match = old_joined_to_new[old_joined_to_new['_merge'] == 'left_only']
no_match = no_match.loc[:, ['collectionCode_old', 'catalogNumber_old', 'scientificName', 'recordedBy_old', 'source', 'original_dataset_id']]
unique_no_match_records = no_match[~no_match['catalogNumber_old'].duplicated(keep=False)]
unique_mapped_lep_records = mapped_lep[~mapped_lep['old_catalog_number'].duplicated(keep=False)]
unambiguous_matches = pd.merge(unique_no_match_records, unique_mapped_lep_records, left_on='catalogNumber_old', right_on='old_catalog_number', how='inner')

print(f'Number of old records we need to match up in the new dataset: {len(old)}')
print(f'Number of exact matches between old catalogue numbers and scientific names: {len(matched_records)}')
print(f'Number of no_match records where there\'s a unique catalogueNumber: {len(unique_no_match_records)}')
print(f'Number of matched_lep records where there\'s a unique old_catalog_number: {len(unique_mapped_lep_records)}')
print(f'Number of no_match records where there\'s a unique and unambiguous match with mapped_lep : {len(unambiguous_matches)}') # This is 0

no_match['collectionCode_old'] = no_match['collectionCode_old'].str.upper()
mapped_lep['old_collection_code'] = mapped_lep['old_collection_code'].str.upper()
matches_on_ccode_ = pd.merge(no_match, mapped_lep, left_on=['collectionCode_old', 'catalogNumber_old'], right_on=['old_collection_code', 'old_catalog_number'], how='inner')
matches_on_ccode_['original_occ_id'] = 'urn:catalog:O:' + matches_on_ccode_['source'] + ':' + matches_on_ccode_['catalogNumber_old'].astype(str)
matches_on_ccode_['new_occ_id'] = matches_on_ccode_['id']
matches_on_ccode = matches_on_ccode_[['original_occ_id', 'new_occ_id', 'original_dataset_id']]

no_match_with_names = no_match.dropna(subset=['recordedBy_old'])
no_match_with_names['surname'] = no_match_with_names['recordedBy_old'].apply(lambda x: x.split(' ')[-1])
mapped_lep_with_names = mapped_lep.dropna(subset=['recordedBy'])
mapped_lep_with_names['surname'] = mapped_lep_with_names['recordedBy'].apply(lambda x: x.split(',')[0])
matches_on_name_ = pd.merge(no_match_with_names, mapped_lep_with_names, left_on=['surname', 'catalogNumber_old'], right_on=['surname', 'old_catalog_number'], how='inner')
matches_on_name_['original_occ_id'] = 'urn:catalog:O:' + matches_on_name_['source'] + ':' + matches_on_name_['catalogNumber_old'].astype(str)
matches_on_name_['new_occ_id'] = matches_on_name_['id']
matches_on_name = matches_on_name_[['original_occ_id', 'new_occ_id', 'original_dataset_id']]

all_matches = pd.concat([matches_on_sn, matches_on_ccode, matches_on_name], ignore_index=True, axis=0)
all_matches.to_csv('merged_ids.csv', index=None)

print(f'Number of matches found: {len(all_matches)}')
print(f'Total number of records in dip, div, het and hym: {len(het) + len(hym) + len(div) + len(dip)}')
print(f'Number of missing matches: {len(het) + len(hym) + len(div) + len(dip) - len(all_matches)}')
import pdb; pdb.set_trace()

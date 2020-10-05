import pandas as pd

# Datasets -
# This one is the main dataset: https://ipt.gbif.no/resource?r=o_lepidoptera
# These two are suspected duplicates: https://ipt.gbif.no/resource?r=o_col, https://ipt.gbif.no/resource?r=o_het
main = pd.read_csv('all-occurrence.txt', sep='\t', dtype=str)
main['surname'] = main['recordedBy'].str.split(' ').str[-1].str.strip()
main.dropna(subset=['recordedBy'], inplace=True)
subset = pd.read_csv('col-occurrence.txt', sep='\t', dtype=str)
subset = pd.read_csv('het-occurrence.txt', sep='\t', dtype=str)
subset['surname'] = subset['recordedBy'].str.split(',').str[0].str.strip()
subset['decimalLatitude'] = subset['decimalLatitude'].str[0:7]
subset['decimalLongitude'] = subset['decimalLongitude'].str[0:7]
subset.dropna(subset=['recordedBy'], inplace=True)
mcols = ['decimalLatitude', 'decimalLongitude', 'year', 'month', 'day', 'surname', 'locality', 'scientificName']
linked = subset.merge(main, how='inner', suffixes=('_s','_m'), on=mcols)
jcols = ['scientificName_m', 'year_m', 'month_m', 'day_m', 'surname_m', 'scientificName_s', 'year_s', 'month_s', 'day_s', 'surname_s']
# linked.reindex(sorted(linked.columns), axis=1)
# temp2 = main.pivot_table(values='scientificName', index=['year', 'surname'], aggfunc='count')
#psubnew = pd.DataFrame([[key[0], key[1], key[2], val] for key, val in psub.to_dict().items()], columns=['year', 'surname', 'scientificName', 'count'])
import pdb; pdb.set_trace()

main = pd.read_csv('all-occurrence.txt', sep='\t')
main['link'] = main['id'].str.split(':').str[4].astype(str)
subset = pd.read_csv('col-occurrence.txt', sep='\t')
subset['link'] = subset['id'].str.split(':').str[4].astype(str)
linked = subset.merge(main, how='left', suffixes=('_s','_m'), on='link')
temp = linked.loc[linked['scientificName_s'] == linked['scientificName_m']] # Only 10
temp[['year_m', 'year_s']] # do not match

subset = pd.read_csv('ent-occurrence.txt', sep='\t')
subset['link'] = subset['id'].str.split(':').str[4].astype(str)
linked = subset.merge(main, how='left', suffixes=('_s','_m'), on='link')
temp = linked.loc[linked['scientificName_s'] == linked['scientificName_m']] # Only 10
import pdb; pdb.set_trace()

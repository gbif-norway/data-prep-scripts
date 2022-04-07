# %%
import datetime
import string
import pandas as pd
from dateutil.parser import parse
import re
import logging
from uuid import uuid4
import numpy as np
# %%
logging.basicConfig(level=logging.INFO)

def extract_name(source: str):
    src_name = []
    source_list = source.split(',')
    for item in source_list:
        if _is_name(item):
            logging.debug(f'Parsing {item} as a name')
            src_name.append(_digest_name(item))
    name_list = [x for x in src_name if x != None]
    return ' | '.join(name_list)

def _is_name(item: str): # [a-zæøå]
    # check if only one word
    item = item.strip()
    if len(re.findall(pattern=r'^([A-Za-zæøå\.]+)$', string=item)) == 1:
        return True
    match_no = len(re.findall(pattern=r'([A-Za-zæøå]+)\.?[\s]*', string=item))
    if match_no > 1:
        return True
    return False

def extract_date(source: str):
    src_date = []
    source_list = source.split(',')
    for item in source_list:
        if _is_date(item):
            logging.debug(f'Parsing {item} as a date')
            src_date.append(_digest_date(item))
    src_date = [x for x in src_date if x != None]
    if len(src_date) == 1:
        return src_date[0]
    if len(src_date) > 1:
        return src_date[-1]
        #raise Exception(f'Multiple dates detected: {source}')
    return None

def _is_date(candidate: str):
    numbers = re.findall(pattern="[0-9]", string=candidate)
    if len(numbers) > 2:
        return True
    return False

def _digest_date(candidate: str):
    # This is for candidates with a month and a year but no day
    if len(re.findall(pattern=r'\w{3,}\.?\s+[0-9]{4}', string=candidate)) == 1:
        spoofed_candidate = f'1. {candidate}'
        try:
            date = parse(spoofed_candidate, fuzzy=True)
            return date.strftime('%Y-%m')
        except Exception as e:
            logging.warning(f'Unable to parse {candidate}\n {e}')

    # Otherwise, just look for numbers to parse as a year
    num_of_digits = len(re.findall(pattern=r'[0-9]', string=candidate))
    if num_of_digits <= 4:
        match = re.findall(pattern=r'[0-9]{4}', string=candidate)
        if match:
            # Exactly 4 digits in row
            return match[0]

    try:
        date = parse(candidate, fuzzy=True, dayfirst=True)
        return date.strftime('%Y-%m-%d')
    except:
        return None


def _digest_name(candidate: str):
    if len(re.findall(pattern=r'[A-Za-zæåø]', string=candidate)) <= 2:
        return None
    return candidate.strip()

def process_dataframe(df: pd.DataFrame): 
    # Drop all rows which have PMO_NR and SUBNO duplicated
    df.drop_duplicates(['PMO_NR', 'SUBNO'], inplace=True, ignore_index=True)

    # Create a catalogNumber (unique ID) for each row based
    df['catalogNumber'] = df['PMO_NR']
    df = df[df['catalogNumber'].notna()]  # Drop all records without a catalogNumber/PMO_NR
    df.loc[df['SUBNO'].notna(), 'catalogNumber'] += '_' + df[df['SUBNO'].notna()]['SUBNO']  # Append the subnumber
    df.drop(['PMO_NR', 'SUBNO'], axis=1, inplace=True)

    # Add the occurrenceIDs, which Dag has suggested we make triplets
    df['occurrenceID'] = 'NHMO:PMO:' + df['catalogNumber']

    # materialSampleID UUID
    df['materialSampleID'] = df['occurrenceID'].apply(lambda x: uuid4())

    # Rename some columns, mostly based on what Eirik did
    mapping = {
            'SPECIES': 'specificEpithet', 
            'GENUS': 'genus',
            'OD': 'scientificNameAuthorship', 
            'country_uk': 'country', 
            'Fylke': 'stateProvince',
            'Kommune': 'county',
            #'': 'scientificName',  # These three seem to have been empty in the spreadsheet from Eirik? 
            #'': 'locality',
            #'': 'lithostratigraphicTerms',
            'GRAD_EAST': 'decimalLongitude',
            'GRAD_NORTH': 'decimalLatitude',
            'FINNER': 'verbatimEventDate',
            'DIVERSE': 'occurrenceRemarks',
            'taxa': 'taxonRemarks', 
            'references': 'materialCitation',
            'TYPE': 'typeStatus', 
            'LATIN': 'scientificName', 
            'LOKALITET': 'locality',
            'STRATIGRAF': 'lithostratigraphicTerms'
            }
    df.rename(columns=mapping, inplace=True) 

    # scientificName seems to sometimes have blank strings e.g. '   ' in... Maybe we should do this for all the cols, idk
    df['scientificName'] = df['scientificName'].replace(r'^\s+$', np.nan, regex=True)

    # Insert taxonRemarks column contents into scientificName column, when we don't have any other info there or in genus
    name_filter = df['genus'].isna() & df['scientificName'].isna()
    df.loc[name_filter, 'scientificName'] = df.loc[name_filter, 'taxonRemarks']  # 57824 rows affected
    len(df[name_filter & df['taxonRemarks'].isna()])  # 2096 rows still without any taxonomic info... I guess that's ok though? We did our best.

    # Date/name extraction
    df['recordedBy'] = df['verbatimEventDate'].fillna('').apply(extract_name)
    df['eventDate'] = df['verbatimEventDate'].fillna('').apply(extract_date)

    return df
# %%
import datetime
import string
import pandas as pd
from dateutil.parser import parse
import re
import logging
# %%
logging.basicConfig(level=logging.INFO)


def extract_names_and_dates(source: pd.Series):
    result_names = source.apply(extract_name)
    result_dates = source.apply(extract_date)
    return result_names, result_dates


def extract_name(source: str):
    src_name = []
    source_list = source.split(',')
    for item in source_list:
        if _is_name(item):
            logging.debug(f'Parsing {item} as a name')
            src_name.append(_digest_name(item))
    return [x for x in src_name if x != None]

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

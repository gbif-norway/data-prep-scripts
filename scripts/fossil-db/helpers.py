# %%
import datetime
import pandas as pd
from dateutil.parser import parse
import re
import logging
# %%
logging.basicConfig(level=logging.DEBUG)


def extract_names_and_dates(source: pd.Series):
    result_names = source.apply(extract_name)
    result_dates = source.apply(extract_date)
    return result_names, result_dates


def extract_name(source: str):
    src_name = []
    source_list = source.split(',')
    for item in source_list:
        if _is_date(item):
            logging.debug(f'Parsing {item} as a date')
        else:
            logging.debug(f'Parsing {item} as a name')
            src_name.append(_digest_name(item))
    return pd.Series(src_name).dropna()


def extract_date(source: str):
    src_date = []
    source_list = source.split(',')
    for item in source_list:
        if _is_date(item):
            logging.debug(f'Parsing {item} as a date')
            src_date.append(_digest_date(item))
        else:
            logging.debug(f'Parsing {item} as a name')
    return pd.Series(src_date).dropna()


def _is_date(candidate: str):
    numbers = re.findall(pattern="[0-9]", string=candidate)
    if len(numbers) > 2:
        return True
    return False


def _digest_date(candidate: str):
    num_of_digits = len(re.findall(pattern=r'[0-9]', string=candidate))
    if num_of_digits <= 4:
        match = re.findall(pattern=r'[0-9]{4}', string=candidate)
        if match:
            # Exactly 4 digits in row
            return match[0]

    try:
        date = parse(candidate, fuzzy=True)
        return date.strftime('%Y-%m-%d')
    except:
        return None


def _digest_name(candidate: str):
    if len(re.findall(pattern=r'[a-z]', string=candidate)) <= 2:
        return None
    return candidate.strip()

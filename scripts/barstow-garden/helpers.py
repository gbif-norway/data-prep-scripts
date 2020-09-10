import re

file_ranges = r'([A-Z][A-Z]?)(\d+)-[A-Z]?[A-Z]?(\d+)\s*\([^)]*?(\d{6})[^)]*\)'
single_file = r'([A-Z][A-Z]?\d+)\s*\([^)]*?(\d{6})[^)]*\)'

def split_rows(comments, occurrenceid):
    new_rows = []
    for match in re.findall(file_ranges, comments):
        file_name_range = range(int(match[1]), int(match[2]) + 1)
        if len(file_name_range) > 10:  # There has been a typo in the ranges
            continue
        for i in file_name_range:
            new_rows.append({'occurrenceid': occurrenceid, 'file_name': match[0] + str(i), 'date': match[3]})
    for match in re.findall(single_file, comments):
        new_rows.append({'occurrenceid': occurrenceid, 'file_name': match[0], 'date': match[1]})
    return new_rows



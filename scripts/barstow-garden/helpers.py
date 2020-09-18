import re

file_ranges = r'([A-Z][A-Z]?)(\d+)-[A-Z]?[A-Z]?(\d+)\s*\(([^)]*?)(\d{6})[^)]*\)'
single_file = r'([A-Z][A-Z]?\d+)\s*\(([^)]*?)(\d{6})[^)]*\)'

def split_rows(comments, taxonid):
    new_rows = []
    for match in re.findall(file_ranges, comments):
        file_name_range = range(int(match[1]), int(match[2]) + 1)
        if len(file_name_range) > 15:  # There has been a typo in the ranges
            continue
        for i in file_name_range:
            new_rows.append({'taxonid': taxonid, 'file_name': match[0] + str(i), 'created': match[4], 'description': match[3].rstrip(' ;')})
    for match in re.findall(single_file, comments):
        new_rows.append({'taxonid': taxonid, 'file_name': match[0], 'created': match[2], 'description': match[1].rstrip(' ;')})
    return new_rows

def merge_duplicate_taxa(df):
    joined_comments = df.groupby(['scientificname'])['comments'].transform(lambda x: '; '.join(x))
    df['comments'] = joined_comments
    return df.drop_duplicates(['scientificname', 'comments'])


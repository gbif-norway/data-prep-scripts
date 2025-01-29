#%%
import pandas as pd
import uuid  # Add this import at the top



# %%
authoreg = pd.read_csv('data/csv/authoreg.csv', dtype=str)
georeg = pd.read_csv('data/csv/georeg.csv', dtype=str)
kryss = pd.read_csv('data/csv/KRYSS.csv', dtype=str)
merknad = pd.read_csv('data/csv/MERKNAD.csv', dtype=str)
taxareg = pd.read_csv('data/csv/TAXAREG.csv', dtype=str)
xl = pd.read_csv('data/csv/XL.csv', dtype=str)
# %%
# %%
merge1 = pd.merge(kryss, xl, on='XLNR', how='left', suffixes=('_kryss', '_xl'))
#%%
# First aggregate merknad records with duplicate keys into JSON lists
merknad_agg = merknad.groupby(['XLNR', 'TAXANR']).agg(lambda x: x.tolist()).reset_index()

# Then merge with merge1, keeping same length as merge1
merge2 = pd.merge(merge1, merknad_agg, on=['XLNR', 'TAXANR'], how='left', suffixes=('', '_merknad'))
# %% 
merge3 = pd.merge(merge2, taxareg, on='TAXANR', how='left', suffixes=('', '_taxareg'))
# %%
merge4 = pd.merge(merge3, authoreg, on='AUTNR', how='left', suffixes=('', '_authoreg'))
# %%
merge4['KOMMNR_xl'] = merge4['KOMMNR_xl'].fillna('-1').astype(float).astype(int).astype(str)
df = pd.merge(merge4, georeg, left_on='KOMMNR_xl',right_on='KOMMNR', how='left', suffixes=('', '_georeg'))
# %%


# %%
e = df.iloc[0]

# %%
def generate_catalog_number(row):
    """Generate catalog number with fallback logic"""
    if pd.notna(row.XLLNR):
        return row.XLLNR
    elif pd.notna(row.XLNR) and pd.notna(row.LNR):
        return f"{row.XLNR}/{int(float(row.LNR))}"
    else:
        return str(uuid.uuid4())
def extract_occurrence(e):
    modified = e.DATO_kryss
    institutionCode = 'O'
    collectionCode = 'VXL'
    basisOfRecord = 'HumanObservation'
    catalogNumber = generate_catalog_number(e)
    occurrenceID = f'urn:catalog:O:VXL:{catalogNumber}'
    try:
        recordedBy = '|'.join([x.strip() for x in e.PERSON.split(',')])
    except:
        recordedBy = e.PERSON
    eventDate = None
    if pd.notna(e.XLDATO):
        try:
            year = int(e.XLDATO[0:4])
            month = int(e.XLDATO[4:6]) 
            day = int(e.XLDATO[6:8])
            eventDate = f'{year:04d}-{month:02d}-{day:02d}'
        except ValueError:
            year = None
            month = None 
            day = None
            eventDate = None
    else:
        year = None
        month = None
        day = None
        eventDate = None
    eventRemarks = e.ARTMERKNAD
    continent = 'Europe'
    country = 'Norway'
    stateProvince = e.FYLKE
    county = e.KOMMUNE
    locality = e.LOKALITET
    minimumElevationInMeters = e.H_O_H_LOW
    maximumElevationInMeters = e.H_O_H_HIGH
    decimalLatitude = e.BREDDE
    decimalLongitude = e.LENGDE
    coordinateUncertaintyInMeters = e.PRECISION
    identifiedBy = recordedBy
    scientificName = e.GNAVN
    verbatimIdentification = e.PRNAVN
    kingdom = 'Plantae'
    dwc_entry = {
        'catalogNumber': catalogNumber,
        'modified': modified,
        'institutionCode': institutionCode,
        'collectionCode': collectionCode,
        'basisOfRecord': basisOfRecord,
        'occurrenceID': occurrenceID,
        'recordedBy': recordedBy,
        'eventDate': eventDate,
        'eventRemarks': eventRemarks,
        'continent': continent,
        'country': country,
        'stateProvince': stateProvince,
        'county': county,
        'locality': locality,
        'minimumElevationInMeters': minimumElevationInMeters,
        'maximumElevationInMeters': maximumElevationInMeters,
        'decimalLatitude': decimalLatitude,
        'decimalLongitude': decimalLongitude,
        'coordinateUncertaintyInMeters': coordinateUncertaintyInMeters,
        'identifiedBy': identifiedBy,
        'scientificName': scientificName,
        'verbatimIdentification': verbatimIdentification,
        'kingdom': kingdom
    }
    return dwc_entry

dwc = df.apply(extract_occurrence, axis=1)

# %%
final_df = pd.DataFrame(list(dwc))
# %%
final_df.to_csv('data/occurrences.csv', index=False)
# %%
df.to_csv('data/merged_original.csv', index=False)
# %%

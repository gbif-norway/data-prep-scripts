import pandas as pd
import uuid

use_cols = {'ref': ['ReferenceID', 'ReferencePage'],
            'original_taxa': ['LatinGenus', 'LatinSpecies', 'InfraSpRank', 'InfraSpName'],
            'accepted_taxa': ['Ataxon', 'ALatinGenus', 'ALatinSpecies', 'AInfraSpRank', 'AInfraSpName'],
            'uses': ['GeneralUses', 'SpecificUses'],
            'other': ['PlantParts', 'Disorders', 'ModeApplication', 'ModeApplicationSpecific', 'Preparation'],
            'distribution': ['GeographicalArea'],
            'common_names': ['VernacularName/s']}
raw = pd.read_excel('GunnerusVSHoeg-data.xlsx', 'Raw', usecols=[item for sublist in use_cols.values() for item in sublist], dtype='str', na_values='-')
raw['taxonID'] = [uuid.uuid4() for x in range(len(raw.index))]

def add_citations(raw):
    hoeg_citation = 'Høeg OA. (1974). Planter og tradisjon: floraen i levende tale og tradisjon i Norge 1925-1973. ISBN 8200089304.'
    raw['ReferenceID'] = raw['ReferenceID'].replace('Høeg_1974', hoeg_citation)
    gunnerus_citation = 'Jørgensen PM, Weidemann E, Fremstad E. (2016). Flora Norvegica av JE Gunnerus. På norsk og med kommentarer. ISBN 978-82-8322-077-3.'
    raw['ReferenceID'] = raw['ReferenceID'].replace('Jørgensen_etal_2016', gunnerus_citation)
    raw.loc[pd.notnull(raw['ReferencePage']), 'ReferenceID'] = raw.loc[pd.notnull(raw['ReferencePage']), 'ReferenceID'] + ' Page: ' +  raw.loc[pd.notnull(raw['ReferencePage']), 'ReferencePage'].astype(str) + '.'
    raw.drop('ReferencePage', inplace=True)
    raw.rename(columns={'ReferenceID': 'references'}, inplace=True)

def create_reference_df(refs):
    refs['type'] = 'checklist'
    refs['language'] = 'nb'

    refs['title'] = 'Flora Norvegica av JE Gunnerus. På norsk og med kommentarer'
    refs['creator'] = 'Jørgensen PM, Weidemann E, Fremstad E'
    refs['date'] = '2016'
    refs['identifier'] = 'ISBN 978-82-8322-077-3'
    refs['bibliographicCitation'] = 'Jørgensen PM, Weidemann E, Fremstad E. (2016). Flora Norvegica av JE Gunnerus. På norsk og med kommentarer. ISBN 978-82-8322-077-3.'

    refs.loc[refs['ReferenceID'] != 'Jørgensen_etal_2016', 'title'] = 'Planter og tradisjon: floraen i levende tale og tradisjon i Norge 1925-1973'
    refs.loc[refs['ReferenceID'] != 'Jørgensen_etal_2016', 'creator'] = 'Ove Arbo Høeg'
    refs.loc[refs['ReferenceID'] != 'Jørgensen_etal_2016', 'date'] = '1974'
    refs.loc[refs['ReferenceID'] != 'Jørgensen_etal_2016', 'identifier'] = 'ISBN 8200089304'
    refs.loc[refs['ReferenceID'] != 'Jørgensen_etal_2016', 'bibliographicCitation'] = 'Høeg OA. (1974). Planter og tradisjon: floraen i levende tale og tradisjon i Norge 1925-1973. ISBN 8200089304.'

    refs['bibliographicCitation'] = refs['bibliographicCitation'] + ' Page: ' + refs['ReferencePage'] + '.'
    return refs.drop(columns=['ReferencePage', 'ReferenceID'])

def _get_gunnerus_vernacular_names(raw_subset):
    # Gunnerus names are in separate spreadsheet with more info, but must be linked back to the TaxonID
    gunnerus_names = pd.read_excel('GunnerusVSHoeg-data.xlsx', 'Gunnerus-Names', usecols=['Ataxon', 'VernacularName/s', 'LanguageID', 'GeographicalArea', 'Meaning', 'Comments'])
    names = raw_subset.merge(gunnerus_names, on='Ataxon')
    names.loc[pd.isnull(names['Meaning']), 'Meaning'] = names['Comments']
    names.drop(columns=['Ataxon', 'Comments'], inplace=True)
    to_iso = {'norw1258': 'no', 'finn1318': 'fi', 'dani1285': 'da', 'swed1254': 'sv', 'stan1295': 'de'}
    return names.rename(columns={'VernacularName/s': 'vernacularName', 'LanguageID': 'language', 'GeographicalArea': 'locality', 'Meaning': 'taxonRemarks'})

def create_vernacular_names_df(raw):
    gunnerus_names = _get_gunnerus_vernacular_names(raw.loc[raw['ReferenceID'] == 'Jørgensen_etal_2016', ['taxonID', 'Ataxon']])
    hoeg_names = raw.loc[raw['ReferenceID'] != 'Jørgensen_etal_2016', ['taxonID', 'VernacularName/s']]
    #hoeg_names = hoeg_names.assign(vernacularName=hoeg_names['VernacularName/s'].str.split(';')).explode('VernacularName/s')
    hoeg_names['VernacularName/s'] = hoeg_names['VernacularName/s'].str.split(';')
    hoeg_names = hoeg_names.explode('VernacularName/s')
    hoeg_names.rename(columns={'VernacularName/s': 'vernacularName'}, inplace=True)
    return pd.concat([gunnerus_names, hoeg_names])

def create_distribution_df(dist):
    dist['locality'] = dist['GeographicalArea'].str.split(';')
    dist = dist.explode('locality')
    return dist.dropna(subset=['locality']).drop(columns='GeographicalArea')

def create_mof_df(mof):
    mof = mof.dropna(subset=['GeneralUses']).copy()
    mof['measurementType'] = 'usage'
    mof['measurementMethod'] = 'see references'
    mof['measurementID'] = [uuid.uuid4() for x in range(len(mof.index))]

    general_uses = {'F': 'food', 'M': 'medicine', 'V': 'veterinary', 'SST': 'social, symbolic and ritual', 'SSR': 'social, symbolic and ritual', 'IC': 'industry and crafts', 'AF': 'animal food', 'Fu': 'fuels', 'Co': 'construction', 'A': 'agricultural', 'O': 'other'}
    mof['GeneralUses'].replace(general_uses, inplace=True)
    mof['measurementValue'] =  mof['GeneralUses'] + ': ' + mof['SpecificUses']
    mof['measurementRemarks'] = mof[use_cols['other']].to_dict(orient='records')
    return mof.drop(columns=use_cols['uses'] + use_cols['other'])

def create_taxon_df(taxa):
    taxa = taxa.dropna(subset['Ataxon']).copy() # There are 6 records with no accepted name, exclude them


# Main
vn_cols = raw[use_cols['common_names'] + ['Ataxon', 'taxonID', 'ReferenceID']]
#create_vernacular_names_df(vn_cols).to_csv('vernacular_names.csv')

#create_reference_df(raw[use_cols['ref'] + ['taxonID']].copy()).to_csv('references.csv')
#create_distribution_df(raw[use_cols['distribution'] + ['taxonID']].copy()).to_csv('distribution.csv')
#create_mof_df(raw[use_cols['uses'] + use_cols['other'] + ['taxonID']].copy()).to_csv('measurement_or_fact.csv')
#create_taxon_df(raw[use_cols['original_taxa'] + use_cols['accepted_taxa'] + ['taxonID']]).to_csv('taxon.csv')





import unittest
from script import create_reference_df, create_vernacular_names_df, create_distribution_df, create_mof_df, create_taxon_df, get_gunnerus_vernacular_names, get_hoeg_vernacular_names
import pandas as pd


class TestCreateReferenceDF(unittest.TestCase):
    def test_it_creates_expected_df(self):
        result = create_reference_df(pd.DataFrame({
            'taxonID': range(0, 4),
            'ReferenceID': ['Jørgensen_etal_2016', 'Jørgensen_etal_2016', 'Jørgensen_etal_2016', 'Høeg_1974'],
            'ReferencePage': ['68', '79', '70-73', '111']
        }))

        hoeg_cit = 'Høeg OA. (1974). Planter og tradisjon: floraen i levende tale og tradisjon i Norge 1925-1973. ISBN 8200089304. Page: '
        gunnar_cit = 'Jørgensen PM, Weidemann E, Fremstad E. (2016). Flora Norvegica av JE Gunnerus. På norsk og med kommentarer. ISBN 978-82-8322-077-3. Page: '
        expected = pd.DataFrame({
            'taxonID': range(0, 4),
            'type': ['checklist'] * 4,
            'language': ['nb'] * 4,
            'title': ['Flora Norvegica av JE Gunnerus. På norsk og med kommentarer'] * 3 + ['Planter og tradisjon: floraen i levende tale og tradisjon i Norge 1925-1973'],
            'creator': ['Jørgensen PM, Weidemann E, Fremstad E'] * 3 + ['Ove Arbo Høeg'],
            'date': ['2016'] * 3 + ['1974'],
            'identifier': ['ISBN 978-82-8322-077-3'] * 3 + ['ISBN 8200089304'],
            'bibliographicCitation': [gunnar_cit + '68.', gunnar_cit + '79.', gunnar_cit + '70-73.', hoeg_cit + '111.']
        })
        pd.testing.assert_frame_equal(result, expected)


class TestCreateVernacularNamesDF(unittest.TestCase):
    def test_get_gunnerus_vernacular_names(self):
        result = get_gunnerus_vernacular_names(
                pd.DataFrame({'taxonID': [1, 2], 'Ataxon': ['Gen1_sp1', 'Gen2_sp2']}),
                pd.DataFrame({
                    'Ataxon': ['Gen1_sp1', 'Gen1_sp1', 'Gen1_sp1', 'Gen2_sp2'],
                    'VernacularName/s': ['Vern1-1', 'Vern1-2', 'Vern1-3', 'Vern2-1'],
                    'LanguageID': ['norw1258', 'stan1295', 'sout2674', 'sout2674'],
                    'GeographicalArea': ['Tromsø,Senja', 'Nidaros', 'Norway', None],
                    'Meaning': ['This name refers to the root', None, None, None],
                    'Comments': [None, 'Variety with purple flowers', None, None]
                    })
                )
        expected = pd.DataFrame({
            'taxonID': [1, 1, 1, 2],
            'vernacularName': ['Vern1-1', 'Vern1-2', 'Vern1-3', 'Vern2-1'],
            'language': ['no', 'de', 'sout2674', 'sout2674'],
            'locality': ['Tromsø,Senja', 'Nidaros', 'Norway', None],
            'taxonRemarks': ['This name refers to the root', 'Variety with purple flowers', None, None]
            })
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

    def test_get_hoeg_vernacular_names(self):
        result = get_hoeg_vernacular_names(pd.DataFrame({
            'taxonID': [1, 2],
            'VernacularName/s': ['mjølauke;mjøldrøye', 'buflog']
            }))
        expected = pd.DataFrame({
            'taxonID': [1, 1, 2],
            'vernacularName': ['mjølauke', 'mjøldrøye', 'buflog']
            })
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


class TestCreateDistributionDF(unittest.TestCase):
    def test_it_creates_expected_df(self):
        result = create_distribution_df(pd.DataFrame({
            'taxonID': range(0, 4),
            'GeographicalArea': ['Akim;Torsnes;Tjølling;Jølster', 'Norway;Sweden', None, 'Denmark']
            }))
        expected = pd.DataFrame({
            'taxonID': [0, 0, 0, 0, 1, 1, 3],
            'locality': ['Akim', 'Torsnes', 'Tjølling', 'Jølster', 'Norway', 'Sweden', 'Denmark']
            })
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


class TestCreateMoFDF(unittest.TestCase):
    def test_it_creates_expected_df(self):
        result = create_mof_df(pd.DataFrame({
            'taxonID': range(0, 5),
            'GeneralUses': ['F', 'Fu', 'Fu', None, 'V'],
            'SpecificUses': ['dyes', 'skin', 'tools', 'dyes', 'dyes'],
            'PlantParts': ['wood', 'seedlings, germinated seeds', None, None, None],
            'Disorders': [None, None, 'nail', None, None],
            'ModeApplication': ['internal', None, None, 'internal', None],
            'ModeApplicationSpecific': ['poultice'] + [None] * 4,
            'Preparation': ['juice'] + [None] * 4
            }))
        expected = pd.DataFrame({
            'taxonID': [0, 1, 2, 4],
            'measurementType': ['usage'] * 4,
            'measurementMethod': ['see references'] * 4,
            'measurementValue': ['food: dyes', 'fuels: skin', 'fuels: tools', 'veterinary: dyes'],
            'measurementRemarks': [
                {'PlantParts': 'wood',                        'Disorders': None,   'ModeApplication': 'internal', 'ModeApplicationSpecific': 'poultice', 'Preparation': 'juice'},
                {'PlantParts': 'seedlings, germinated seeds', 'Disorders': None,   'ModeApplication': None,       'ModeApplicationSpecific': None,        'Preparation': None},
                {'PlantParts': None,                          'Disorders': 'nail', 'ModeApplication': None,       'ModeApplicationSpecific': None,        'Preparation': None},
                {'PlantParts': None,                          'Disorders': None,   'ModeApplication': None,       'ModeApplicationSpecific': None,        'Preparation': None},
                ]
            })
        self.assertTrue('measurementID' in result.columns)
        pd.testing.assert_frame_equal(result.drop(columns='measurementID').reset_index(drop=True), expected)


class TestCreateTaxonDF(unittest.TestCase):
    def test_it_creates_expected_df(self):
        result = create_taxon_df(pd.DataFrame({
            'taxonID': [1, 2, 3],
            'Ataxon': ['Gen_sp', None, 'Gen3_sp3'],
            'LatinGenus': ['Old_gen', None, 'Old3_gen'],
            'LatinSpecies': ['old_sp', None, 'old3_sp'],
            'InfraSpRank': [None, None, 'var.'],
            'InfraSpName': [None, None, 'Old3_var'],
            'ALatinGenus': ['Gen1', None, 'Gen3'],
            'ALatinSpecies': ['sp1', None, 'sp3'],
            'AInfraSpRank': [None, None, 'subsp.'],
            'AInfraSpName': [None, None, 'newsubsp']
        }))
        expected = pd.DataFrame({
            'taxonID': [1, 3],
            'genus': ['Gen1', 'Gen3'],
            'specificEpithet': ['sp1', 'sp3'],
            'verbatimTaxonRank': [None, 'subsp.'],
            'infraspecificEpithet': [None, 'newsubsp'],
            'scientificName': ['Old_gen old_sp', 'Old3_gen old3_sp var. Old3_var'],
            'acceptedNameUsage': ['Gen1 sp1', 'Gen3 sp3 subsp. newsubsp'],
            })
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


if __name__ == "__main__":
    unittest.main()

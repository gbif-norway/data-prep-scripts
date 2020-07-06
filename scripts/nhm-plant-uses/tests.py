import unittest
from script import create_reference_df, create_vernacular_names_df, create_distribution_df, create_mof_df, create_taxon_df, get_gunnerus_vernacular_names, get_hoeg_vernacular_names
import pandas as pd
import numpy as np


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
                    'GeographicalArea': ['Tromsø,Senja', 'Nidaros', 'Norway', np.nan],
                    'Meaning': ['This name refers to the root', np.nan, np.nan, np.nan],
                    'Comments': [np.nan, 'Variety with purple flowers', np.nan, np.nan]
                    })
                )
        expected = pd.DataFrame({
            'taxonID': [1, 1, 1, 2],
            'vernacularName': ['Vern1-1', 'Vern1-2', 'Vern1-3', 'Vern2-1'],
            'language': ['no', 'de', 'sout2674', 'sout2674'],
            'locality': ['Tromsø,Senja', 'Nidaros', 'Norway', np.nan],
            'taxonRemarks': ['This name refers to the root', 'Variety with purple flowers', np.nan, np.nan]
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
            'GeographicalArea': ['Akim;Torsnes;Tjølling;Jølster', 'Norway;Sweden', np.nan, 'Denmark']
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
            'GeneralUses': ['F', 'Fu', 'Fu', np.nan, 'V'],
            'SpecificUses': ['dyes', 'skin', 'tools', 'dyes', 'dyes'],
            'PlantParts': ['wood', 'seedlings, germinated seeds', np.nan, np.nan, np.nan],
            'Disorders': [np.nan, np.nan, 'nail', np.nan, np.nan],
            'ModeApplication': ['internal', np.nan, np.nan, 'internal', np.nan],
            'ModeApplicationSpecific': ['poultice'] + [np.nan] * 4,
            'Preparation': ['juice'] + [np.nan] * 4
            }))
        expected = pd.DataFrame({
            'taxonID': [0, 1, 2, 4],
            'measurementType': ['usage'] * 4,
            'measurementMethod': ['see references'] * 4,
            'measurementValue': ['food: dyes', 'fuels: skin', 'fuels: tools', 'veterinary: dyes'],
            'measurementRemarks': [
                {'PlantParts': 'wood', 'ModeApplication': 'internal', 'ModeApplicationSpecific': 'poultice', 'Preparation': 'juice'},
                {'PlantParts': 'seedlings, germinated seeds'},
                {'Disorders': 'nail'},
                {}
                ]
            })
        self.assertTrue('measurementID' in result.columns)
        pd.testing.assert_frame_equal(result.drop(columns='measurementID').reset_index(drop=True), expected)


class TestCreateTaxonDF(unittest.TestCase):
    def test_it_creates_expected_df(self):
        result = create_taxon_df(pd.DataFrame({
            'taxonID': [1, 2, 3],
            'Ataxon': ['Gen_sp', np.nan, 'Gen3_sp3'],
            'LatinGenus': ['Old_gen', np.nan, 'Old3_gen'],
            'LatinSpecies': ['old_sp', np.nan, 'old3_sp'],
            'InfraSpRank': [np.nan, np.nan, 'var.'],
            'InfraSpName': [np.nan, np.nan, 'Old3_var'],
            'ALatinGenus': ['Gen1', np.nan, 'Gen3'],
            'ALatinSpecies': ['sp1', np.nan, 'sp3'],
            'AInfraSpRank': [np.nan, np.nan, 'subsp.'],
            'AInfraSpName': [np.nan, np.nan, 'newsubsp']
        }))
        expected = pd.DataFrame({
            'taxonID': [1, 3],
            'genus': ['Gen1', 'Gen3'],
            'specificEpithet': ['sp1', 'sp3'],
            'verbatimTaxonRank': [np.nan, 'subsp.'],
            'infraspecificEpithet': [np.nan, 'newsubsp'],
            'scientificName': ['Old_gen old_sp', 'Old3_gen old3_sp var. Old3_var'],
            'acceptedNameUsage': ['Gen1 sp1', 'Gen3 sp3 subsp. newsubsp'],
            })
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)


if __name__ == "__main__":
    unittest.main()

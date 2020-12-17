import unittest
from helpers import split_rows, merge_duplicate_taxa, get_date
import pandas as pd
from pandas._testing import assert_frame_equal, assert_series_equal
from unittest.mock import patch
from uuid import uuid4
import uuid


class GetSensibleDate(unittest.TestCase):
    def test_constructs_date(self):
        year, month, day  = pd.Series(['19', '20']), pd.Series(['09', '11']), pd.Series(['01', '02'])
        expected = pd.Series(['2019-09-01', '2020-11-02'])
        assert_series_equal(get_date(year, month, day), expected)

    def test_handles_1990s(self):
        year, month, day  = pd.Series(['98', '10']), pd.Series(['09', '11']), pd.Series(['01', '02'])
        expected = pd.Series(['1998-09-01', '2010-11-02'])
        assert_series_equal(get_date(year, month, day), expected)


class MergeDuplicateTaxa(unittest.TestCase):
    # There should be 1 row per taxon, if there isn't then there is a mistake, merge them
    def test_returns_merged_taxa(self):
        input_df = pd.DataFrame({'scientificname': ['a', 'b', 'a'], 'comments': ['E313 (030904)', 'P477-479 (100408)', 'P21636-21637 (This?; 300711);']})
        expected_df = pd.DataFrame({'scientificname': ['a', 'b'], 'comments': ['E313 (030904); P21636-21637 (This?; 300711);', 'P477-479 (100408)']})
        assert_frame_equal(merge_duplicate_taxa(input_df), expected_df)

class TestSplitRows(unittest.TestCase):
    def test_example1(self):
        eg = 'P42253-42255 (Received bulbs; 040713)'
        expected = [{'taxonid': 'id1', 'file_name': 'P42253', 'created': '040713', 'description': 'Received bulbs'}, {'taxonid': 'id1', 'file_name': 'P42254', 'created': '040713', 'description': 'Received bulbs'}, {'taxonid': 'id1', 'file_name': 'P42255', 'created': '040713', 'description': 'Received bulbs'}]
        self.assertEqual(split_rows(eg, 'id1'), expected)

    def test_it_splits_simple_file_names_and_dates(self):
        eg = 'IM1032 (120807); HP1231 (110907)'
        expected = [{'taxonid': 'id1', 'file_name': 'IM1032', 'created': '120807', 'description': ''}, {'taxonid': 'id1', 'file_name': 'HP1231', 'created': '110907', 'description': ''}]
        self.assertEqual(split_rows(eg, 'id1'), expected)

    def test_it_does_not_create_rows_for_incorrect_formats(self):
        eg = 'E560 (PBS - Early 90s?); SA501 (Sept. 98); E34 (03)'
        self.assertEqual(split_rows(eg, 'id1'), [])

    def test_it_does_not_create_rows_for_incorrect_formats_when_mixed_with_valid_1(self):
        eg = 'E560 (PBS - Early 90s?); SA501 (Sept. 98); P3643 (130708);'
        self.assertEqual(split_rows(eg, 'id1'), [{'taxonid': 'id1', 'file_name': 'P3643', 'created': '130708', 'description': ''}])

    def test_it_does_not_create_rows_for_incorrect_formats_when_mixed_with_valid_2(self):
        eg = 'P3643 (130708); E560 (PBS - Early 90s?); SA501 (Sept. 98)'
        self.assertEqual(split_rows(eg, 'id1'), [{'taxonid': 'id1', 'file_name': 'P3643', 'created': '130708', 'description': ''}])

    def test_it_does_not_create_rows_for_incorrect_formats_when_mixed_with_valid_3(self):
        eg = 'P3643 (130708); E560 (PBS - Early 90s?); P3642 (150708); SA501 (Sept. 98)'
        self.assertEqual(split_rows(eg, 'id1'), [{'taxonid': 'id1', 'file_name': 'P3643', 'created': '130708', 'description': ''}, {'taxonid': 'id1', 'file_name': 'P3642', 'created': '150708', 'description': ''}])

    def test_it_does_not_break_with_non_date_numbers_in_brackets(self):
        eg = 'P6017 (Self-Seeded on this bed 08; 240808);'
        self.assertEqual(split_rows(eg, 'id1'), [{'taxonid': 'id1', 'file_name': 'P6017', 'created': '240808', 'description': 'Self-Seeded on this bed 08'}])

    def test_file_name_ranges_only(self):
        eg = 'HP5850-5854 (4 different blue Acaenas; 240906); P33976-33977 (Acaena argentea and Pulmonaria; 290612)'
        expected = [
                {'taxonid': 'id1', 'file_name': 'HP5850', 'created': '240906', 'description': '4 different blue Acaenas'},
                {'taxonid': 'id1', 'file_name': 'HP5851', 'created': '240906', 'description': '4 different blue Acaenas'},
                {'taxonid': 'id1', 'file_name': 'HP5852', 'created': '240906', 'description': '4 different blue Acaenas'},
                {'taxonid': 'id1', 'file_name': 'HP5853', 'created': '240906', 'description': '4 different blue Acaenas'},
                {'taxonid': 'id1', 'file_name': 'HP5854', 'created': '240906', 'description': '4 different blue Acaenas'},
                {'taxonid': 'id1', 'file_name': 'P33976', 'created': '290612', 'description': 'Acaena argentea and Pulmonaria'},
                {'taxonid': 'id1', 'file_name': 'P33977', 'created': '290612', 'description': 'Acaena argentea and Pulmonaria'},
                ]
        self.assertEqual(split_rows(eg, 'id1'), expected)

    def test_file_name_ranges_mixed_with_file_names_and_incorrect_formats(self):
        eg = 'E560 (PBS - Early 90s?); SA501 (Sept. 98); HP5850-5854 (4 different blue Acaenas; 240906); P3643 (130708); IM3099 (Edinburgh Botanics; 151009);  P33976-33977 (Acaena argentea and Pulmonaria; 290612)'
        expected = [
                {'taxonid': 'id1', 'file_name': 'HP5850', 'created': '240906', 'description': '4 different blue Acaenas'},
                {'taxonid': 'id1', 'file_name': 'HP5851', 'created': '240906', 'description': '4 different blue Acaenas'},
                {'taxonid': 'id1', 'file_name': 'HP5852', 'created': '240906', 'description': '4 different blue Acaenas'},
                {'taxonid': 'id1', 'file_name': 'HP5853', 'created': '240906', 'description': '4 different blue Acaenas'},
                {'taxonid': 'id1', 'file_name': 'HP5854', 'created': '240906', 'description': '4 different blue Acaenas'},
                {'taxonid': 'id1', 'file_name': 'P33976', 'created': '290612', 'description': 'Acaena argentea and Pulmonaria'},
                {'taxonid': 'id1', 'file_name': 'P33977', 'created': '290612', 'description': 'Acaena argentea and Pulmonaria'},
                {'taxonid': 'id1', 'file_name': 'P3643', 'created': '130708', 'description': ''},
                {'taxonid': 'id1', 'file_name': 'IM3099', 'created': '151009', 'description': 'Edinburgh Botanics'},
                ]
        self.assertEqual(split_rows(eg, 'id1'), expected)

    def test_discards_image_ranges_with_typos(self):
        eg = 'P32023-39027 (Picked Polygonum amphibium, variegated Allium nutans? and Sanguisorba spp; 210513)'
        self.assertEqual(split_rows(eg, 'id1'), [])


if __name__ == "__main__":
    unittest.main()


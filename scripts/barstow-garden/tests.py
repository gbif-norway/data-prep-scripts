import unittest
from helpers import split_rows
import pandas as pd


class TestSplitRows(unittest.TestCase):
    def test_it_splits_simple_file_names_and_dates(self):
        eg = 'IM1032 (120807); HP1231 (110907)'
        expected = [{'occurrenceid': 'id1', 'file_name': 'IM1032', 'date': '120807'}, {'occurrenceid': 'id1', 'file_name': 'HP1231', 'date': '110907'}]
        self.assertEqual(split_rows(eg, 'id1'), expected)

    def test_it_does_not_create_rows_for_incorrect_formats(self):
        eg = 'E560 (PBS - Early 90s?); SA501 (Sept. 98); E34 (03)'
        self.assertEqual(split_rows(eg, 'id1'), [])

    def test_it_does_not_create_rows_for_incorrect_formats_when_mixed_with_valid_1(self):
        eg = 'E560 (PBS - Early 90s?); SA501 (Sept. 98); P3643 (130708);'
        self.assertEqual(split_rows(eg, 'id1'), [{'occurrenceid': 'id1', 'file_name': 'P3643', 'date': '130708'}])

    def test_it_does_not_create_rows_for_incorrect_formats_when_mixed_with_valid_2(self):
        eg = 'P3643 (130708); E560 (PBS - Early 90s?); SA501 (Sept. 98)'
        self.assertEqual(split_rows(eg, 'id1'), [{'occurrenceid': 'id1', 'file_name': 'P3643', 'date': '130708'}])

    def test_it_does_not_create_rows_for_incorrect_formats_when_mixed_with_valid_3(self):
        eg = 'P3643 (130708); E560 (PBS - Early 90s?); P3642 (150708); SA501 (Sept. 98)'
        self.assertEqual(split_rows(eg, 'id1'), [{'occurrenceid': 'id1', 'file_name': 'P3643', 'date': '130708'}, {'occurrenceid': 'id1', 'file_name': 'P3642', 'date': '150708'}])

    def test_it_does_not_break_with_non_date_numbers_in_brackets(self):
        eg = 'P6017 (Self-Seeded on this bed 08; 240808);'
        self.assertEqual(split_rows(eg, 'id1'), [{'occurrenceid': 'id1', 'file_name': 'P6017', 'date': '240808'}])

    def test_file_name_ranges(self):
        eg = 'HP5850-5854 (4 different blue Acaenas; 240906); P33976-33977 (Acaena argentea and Pulmonaria; 290612)'
        expected = [
                {'occurrenceid': 'id1', 'file_name': 'HP5850', 'date': '240906'},
                {'occurrenceid': 'id1', 'file_name': 'HP5851', 'date': '240906'},
                {'occurrenceid': 'id1', 'file_name': 'HP5852', 'date': '240906'},
                {'occurrenceid': 'id1', 'file_name': 'HP5853', 'date': '240906'},
                {'occurrenceid': 'id1', 'file_name': 'HP5854', 'date': '240906'},
                {'occurrenceid': 'id1', 'file_name': 'P33976', 'date': '290612'},
                {'occurrenceid': 'id1', 'file_name': 'P33977', 'date': '290612'},
                ]
        self.assertEqual(split_rows(eg, 'id1'), expected)

    def test_file_name_ranges_mixed_with_file_names_and_incorrect_formats(self):
        eg = 'E560 (PBS - Early 90s?); SA501 (Sept. 98); HP5850-5854 (4 different blue Acaenas; 240906); P3643 (130708); IM3099 (Edinburgh Botanics; 151009);  P33976-33977 (Acaena argentea and Pulmonaria; 290612)'
        expected = [
                {'occurrenceid': 'id1', 'file_name': 'HP5850', 'date': '240906'},
                {'occurrenceid': 'id1', 'file_name': 'HP5851', 'date': '240906'},
                {'occurrenceid': 'id1', 'file_name': 'HP5852', 'date': '240906'},
                {'occurrenceid': 'id1', 'file_name': 'HP5853', 'date': '240906'},
                {'occurrenceid': 'id1', 'file_name': 'HP5854', 'date': '240906'},
                {'occurrenceid': 'id1', 'file_name': 'P33976', 'date': '290612'},
                {'occurrenceid': 'id1', 'file_name': 'P33977', 'date': '290612'},
                {'occurrenceid': 'id1', 'file_name': 'P3643', 'date': '130708'},
                {'occurrenceid': 'id1', 'file_name': 'IM3099', 'date': '151009'},
                ]
        self.assertEqual(split_rows(eg, 'id1'), expected)

    def test_discards_image_ranges_with_typos(self):
        eg = 'P32023-39027 (Picked Polygonum amphibium, variegated Allium nutans? and Sanguisorba spp; 210513)'
        self.assertEqual(split_rows(eg, 'id1'), [])


if __name__ == "__main__":
    unittest.main()


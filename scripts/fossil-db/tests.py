import unittest
import pandas as pd
from pandas._testing import assert_frame_equal, assert_series_equal
from helpers import extract_name, extract_date

class DateExtraction(unittest.TestCase):
    def test_names_general(self):
        expected = pd.Series(['G. Henningsmoen', 'T.G. Bockelie'])
        result = extract_name('G. Henningsmoen, T.G. Bockelie, 15-4-1978.')
        assert_series_equal(expected, result)

    def test_dates_general(self):
        expected = pd.Series(['1978-04-15'])
        result = extract_date('G. Henningsmoen, T.G. Bockelie, 15-4-1978.')
        assert_series_equal(expected, result)

    def test_dot_delimiter(self):
        expected = pd.Series(['1933-08-30'])
        result = extract_date('T.Strand, 30.8.1933')
        assert_series_equal(expected, result)

    def test_year_only(self):
        result = extract_date('Bjorn T. Larsen, 1974  (?)')
        expected = pd.Series(['1974'])
        assert_series_equal(expected, result)

    def test_name_with_date_question_mark(self):
        result = extract_name('Bjorn T. Larsen, 1974  (?)')
        expected = pd.Series(['Bjorn T. Larsen'])
        assert_series_equal(expected, result)

    def test_hyphen_slash_mix_names(self):
        result = extract_name('J. Kiær, 2/9-1915')
        expected = pd.Series(['J. Kiær'])
        assert_series_equal(expected, result)

    def test_hyphen_slash_mix_dates(self):
        result = extract_date('J. Kiær, 2/9-1915')
        expected = pd.Series(['1915-02-09'])
        assert_series_equal(expected, result)

    def test_no_name(self):  # 'Bockelie og Briskeby, ----'
        result = extract_name('----, 1932')
        expected = pd.Series()
        self.assertTrue(result.empty)

    def test_no_date(self):  
        result = extract_date('Bockelie og Briskeby, ----')
        expected = pd.Series()
        self.assertTrue(result.empty)

    # Not tested below

    def test_string_dates(self):
        source = pd.Series(['Johan Kiær, september 1913', 'Bockelie, sept. 1971', 'Johan Kiær, 10. september - 1898.'])
        expected_dates = pd.Series(['Johan Kiær', 'Bockelie', 'Johan Kiær'])
        expected_names = pd.Series(['1913-09', '1971-09', '1898-09-10'])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    def test_0_padded(self):
        source = pd.Series(['D. L. Bruton & B. Wandås, 22.05.1979.'])
        expected_dates = pd.Series(['1979-05-22'])
        expected_names = pd.Series(['D. L. Bruton & B. Wandås'])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    def _test_remove_random_words(self):  # Maybe rather ambitious!!
        source = pd.Series(['Kjopt av Anders Eriksen den 5-5-1900.'])
        expected_dates = pd.Series(['Anders Eriksen'])
        expected_names = pd.Series(['1900-05-05'])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    def test_dates_only(self):
        source = pd.Series(['1873?', '15/9/1948'])
        expected_dates = pd.Series(['1873', '1948-09-15'])
        expected_names = pd.Series(['', ''])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    def test_date_ranges(self):  # Do we actually want to try do this? I guess if the fancy dateutil parse can handle it, why not...
        source = pd.Series(['N.Spjeldnæs, 19??', 'Helbert,1983-85.'])
        expected_dates = pd.Series(['1900/1999', '1983/1985'])
        expected_names = pd.Series(['N.Spjeldnæs', 'Helbert'])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    # Johan Kiær, hosten 1914. - do we want to do anything about seasons?
    # A common theme is presents/gave, maybe it's worth writing some rule for these? e.g. 'Gave fra Egil Berntsen, mai 1965.', 'Gave fra U. Of Minnesota', 'Gave, H.H.Horneman, 1924.', 'Formann Henry Holt (gave 1957)'


    def _test_template(self):
        source = pd.Series([''])
        expected_dates = pd.Series([''])
        expected_names = pd.Series([''])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

if __name__ == "__main__":
    unittest.main()
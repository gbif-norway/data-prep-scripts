import unittest
import pandas as pd
from pandas._testing import assert_frame_equal, assert_series_equal

class DateExtraction(unittest.TestCase):
    def test_hyphenated(self):
        source = pd.Series(['G. Henningsmoen, T.G. Bockelie, 15-4-1978.'])
        expected_dates = pd.Series(['1978-04-15'])
        expected_names = pd.Series(['G. Henningsmoen, T.G. Bockelie'])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    def test_dot_delimiter(self):
        source = pd.Series(['T.Strand, 30.8.1933'])
        expected_dates = pd.Series(['1933-08-30'])
        expected_names = pd.Series(['T.Strand'])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    def test_year_only(self):
        source = pd.Series(['Bjorn T. Larsen, 1974  (?)'])
        expected_dates = pd.Series(['1974'])
        expected_names = pd.Series(['Bjorn T. Larsen'])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    def test_hyphen_slash_mix(self):
        source = pd.Series(['J. Kiær, 2/9-1915'])  # 'EKSKURSJON 10/6-1926'
        expected_dates = pd.Series(['1915-09-02'])
        expected_names = pd.Series(['J. Kiær'])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    def test_no_date(self):
        source = pd.Series(['Bockelie og Briskeby, ----'])
        expected_dates = pd.Series([''])
        expected_names = pd.Series(['Bockelie og Briskeby'])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    def test_string_dates(self):
        source = pd.Series(['Johan Kiær, september 1913'], ['Bockelie, sept. 1971'])
        expected_dates = pd.Series(['Johan Kiær'], ['Bockelie'])
        expected_names = pd.Series(['1913-09'], ['1971-09'])
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
        source = pd.Series(['1873?'])
        expected_dates = pd.Series(['1873'])
        expected_names = pd.Series([''])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    def test_date_ranges(self):
        source = pd.Series(['N.Spjeldnæs, 19??', 'Helbert,1983-85.'])
        expected_dates = pd.Series(['1900/1999', '1983/1985'])
        expected_names = pd.Series(['N.Spjeldnæs', 'Helbert'])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

    # Johan Kiær, hosten 1914. - do we want to do anything about seasons?

    def _test_template(self):
        source = pd.Series([''])
        expected_dates = pd.Series([''])
        expected_names = pd.Series([''])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

import unittest
import pandas as pd
from pandas._testing import assert_frame_equal, assert_series_equal
from helpers import extract_name, extract_date

class DateExtraction(unittest.TestCase):
    def test_names_general(self):
        result = extract_name('G. Henningsmoen, T.G. Bockelie, 15-4-1978.')
        self.assertEqual('G. Henningsmoen | T.G. Bockelie', result)

    def test_dates_general(self):
        result = extract_date('G. Henningsmoen, T.G. Bockelie, 15-4-1978.')
        self.assertEqual('1978-04-15', result)

    def test_dot_delimiter(self):
        result = extract_date('T.Strand, 30.8.1933')
        self.assertEqual('1933-08-30', result)

    def test_year_only(self):
        result = extract_date('Bjorn T. Larsen, 1974  (?)')
        self.assertEqual('1974', result)

    def test_name_with_date_question_mark(self):
        result = extract_name('Bjorn T. Larsen, 1974  (?)')
        self.assertEqual('Bjorn T. Larsen', result)

    def test_hyphen_slash_mix_names(self):
        result = extract_name('J. Kiær, 2/9-1915')
        self.assertEqual('J. Kiær', result)

    def test_hyphen_slash_mix_dates(self):
        result = extract_date('J. Kiær, 2/9-1915')
        self.assertEqual('1915-09-02', result)

    def test_no_name(self):  # 'Bockelie og Briskeby, ----'
        result = extract_name('----, 1932')
        self.assertEqual(result, '')

    def test_no_date(self):  
        result = extract_date('Bockelie og Briskeby, ----')
        self.assertEqual(result, None)

    def test_string_names(self):
        sources = ['Johan Kiær, september 1913', 'Bockelie, sept. 1971', 'Johan Kiær, 10. september - 1898.']
        expecteds = ['Johan Kiær', 'Bockelie', 'Johan Kiær']
        for idx, source in enumerate(sources):
            result = extract_name(source)
            self.assertEqual(expecteds[idx], result)

    def test_string_dates(self):
        sources = ['Johan Kiær, september 1913', 'Bockelie, sept. 1971', 'Johan Kiær, 10. september - 1898.']
        expecteds = ['1913-09', '1971-09', '1898-09-10']
        for idx, source in enumerate(sources):
            result = extract_date(source)
            self.assertEqual(expecteds[idx], result)

    def test_0_padded(self):
        source = 'D. L. Bruton & B. Wandås, 22.05.1979.'
        self.assertEqual('1979-05-22', extract_date(source))

    def test_no_comma_date(self):
        source = 'Kjopt av Anders Eriksen den 5-5-1900.'
        self.assertEqual('1900-05-05', extract_date(source))

    def test_no_comma_name(self):
        source = 'Kjopt av Anders Eriksen den 5-5-1900.'
        self.assertEqual('Kjopt av Anders Eriksen den 5-5-1900.', extract_name(source))

    def test_dates_only(self):
        sources = ['1873?', '5/9/1948']
        expecteds = ['1873', '1948-09-05']
        for idx, source in enumerate(sources):
            result = extract_date(source)
            self.assertEqual(expecteds[idx], result)

    def test_date_ranges(self):  # Do we actually want to try do this? I guess if the fancy dateutil parse can handle it, why not...
        sources = ['N.Spjeldnæs, 19??', 'Helbert,1983-85.']
        expecteds = [None, None]  # '1900/1999' maybe?
        for idx, source in enumerate(sources):
            result = extract_date(source)
            self.assertEqual(expecteds[idx], result)

    def test_seasons_names(self):  # verbatimEventDate will capture the seasons info
        sources = ['J. Kiær, hosten 1914.', 'Tove Bockelie, våren 1972.']
        expecteds = ['J. Kiær', 'Tove Bockelie']
        for idx, source in enumerate(sources):
            result = extract_name(source)
            self.assertEqual(expecteds[idx], result)
    
    def test_name_with_slashes(self):
        source = 'Williams/Bruton, 1982.'
        self.assertEqual('Williams/Bruton', extract_name(source))
    
    def test_name_with_parenthesis(self):
        source = '1938 (sendt av H. Hoff, 6.5.1943)'
        self.assertEqual('1938 (sendt av H. Hoff', extract_name(source))

    def test_multiple_dates(self):
        source = '1938 (sendt av H. Hoff, 6.5.1943)'
        self.assertEqual('1943-05-06', extract_date(source))

    def test_multiple_people(self):
        source = 'test, test'
        self.assertEqual('test | test', extract_name(source))

    # A common theme is presents/gave, maybe it's worth writing some rule for these? e.g. 'Gave fra Egil Berntsen, mai 1965.', 'Gave fra U. Of Minnesota', 'Gave, H.H.Horneman, 1924.', 'Formann Henry Holt (gave 1957)'
    #J.Kiær. juli 1914
# J.Kiær. 12.07.1920

    def _test_template(self):
        source = pd.Series([''])
        expected_dates = pd.Series([''])
        expected_names = pd.Series([''])
        result_names, result_dates = extract_names_and_dates(source)
        assert_series_equal(expected_dates, result_dates)
        assert_series_equal(expected_names, result_names)

if __name__ == "__main__":
    unittest.main()
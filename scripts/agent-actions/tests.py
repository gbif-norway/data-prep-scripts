import pandas as pd
import unittest
import helpers

class TestMakeDate(unittest.TestCase):
    def test_three_variations(self):
        years = pd.Series(['2019', '1700', '2050'])
        months = pd.Series(['01', '', '12'])
        days = pd.Series(['01', '', ''])
        expected = pd.Series(['2019-01-01', '1700', '2050-12'])
        result = helpers.make_date(years, months, days)
        self.assertEqual(result[0], expected[0])
        self.assertEqual(result[1], expected[1])
        self.assertEqual(result[2], expected[2])

if __name__=="__main__":
    unittest.main()

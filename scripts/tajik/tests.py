import unittest
from script import standardise_names

class StandardiseNames(unittest.TestCase):
    def test_im_lazy(self):
        cases = {
        'Stanjukovicz, K, Sidorov,L Ladigina, G. Ikonnikov,S.': 'Stanjukovicz K. | Sidorov L. | Ladigina G. | Ikonnikov S.',
        'Kinzikaeva, G.K. Ryabkova, L.S.': 'Kinzikaeva G.K. | Ryabkova L.S.',
        'Mashevskaya,S.G; Kostuchenko, R.D.': 'Mashevskaya S.G | Kostuchenko R.D.',
        'Zavedeev, B. H.': 'Zavedeev B.H.',
        'Ismatova,': 'Ismatova',
        'Bachmut,; Mansurov ; Chukavin': 'Bachmut | Mansurov | Chukavin',
        'Stanjukovich, K.     Sidorov,L.;Ladigina,G.; Ikonnikov,S': 'Stanjukovich K. | Sidorov L. | Ladigina G. | Ikonnikov S.',
        'Ryabkova,Zogolova,': 'Ryabkova | Zogolova',
        'Ashurmukhamedov.': 'Ashurmukhamedov',
        'T.J. Maslennikova': 'Maslennikova',  # Do we want to bother with doing this properly?
        # 'Ryabkova, T.J. Maslennikova, Sidorov,L.': 'Ryabkova | Maslennikova T.J. | Sidorov L.'  # Or this?
        'Zaprigaeva, V.I. Ilinskaya, K.S.': 'Zaprigaeva V.I. | Ilinskaya K.S.',
        'Zabolockaya, R.P. Ilinskaya,K. S.': 'Zabolockaya, R.P. | Ilinskaya K.S.'
        }
    for input, expected in cases.items():
        self.assertEqual(standardise_names(input), expected)

if __name__ == "__main__":
    unittest.main()

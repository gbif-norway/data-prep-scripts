import logging
from helpers import Biorehab

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

    biorehab = Biorehab('input/Biorehab Klepsland_Norge_1.xlsx')
    biorehab.add_missing_occurrence_ids()
    biorehab.trim_for_dwc_publication()

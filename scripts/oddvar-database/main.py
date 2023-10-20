#%%
import pandas as pd
from simpledbf import Dbf5
from pathlib import Path
from dbfread import DBF
# %%
orig_input = Path('data/orig')
# %%
orig_dbfs = list(orig_input.glob(r'*[dD][bB][fF]'))
# %%

orig_dbfs
# %%
fmap = {}
for dbf_file in orig_dbfs:
    dbf = DBF(dbf_file, encoding='iso-8859-1')
    df = pd.DataFrame(iter(dbf))
    fmap[dbf_file.name] = df


# %%
import pandas as pd
import io
import os
from .sazPure import updated_nm, make_report

def make_csv(dfrm, file_name, file_path=None):
    dest = os.path.join(file_path, file_name)
    dfrm.to_csv(dest, index=False, encoding='utf-8')

def tbl_schema(dfrm):
    dfrm = pd.DataFrame(dfrm)
    buffer = io.StringIO()
    dfrm.info(buf=buffer)
    schema = buffer.getvalue()
    f_name = updated_nm('schema', 'txt')
    make_report(f_name, schema)

def tbl_cardin(dfrm):
    cardins = 'This is the cardinality report of table. \n\n'
    for col in dfrm.columns:
        cardin = dfrm[col].value_counts().to_string()
        cardins += f'The cardinality of *{col}* is:\n{cardin}\n'
    print(cardins)
    f_name = updated_nm('cardinality', 'txt')
    make_report(f_name, cardins)
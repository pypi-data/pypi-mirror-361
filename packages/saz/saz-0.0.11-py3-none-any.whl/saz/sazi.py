import io
import os
import pandas as pd
from datetime import date
import logging

logger = logging.getLogger(__name__)

# This function generates a filename by appending the current date to a base name and format.
def updated_name_with_date(initial, frmt):
    today = date.today()
    tdyfrmt = today.strftime('%Y%m%d')
    upname = initial + '_report_' + tdyfrmt + '.' + frmt
    return upname

# This function creates a text report file with the given content.
def make_report(file_name, content):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(content)
    pass

# This function creates a CSV file from the provided DataFrame.
def make_csv(dfrm, file_name, file_path=None):
    dest = os.path.join(file_path, file_name)
    dfrm.to_csv(dest, index=False, encoding='utf-8')
    pass

# This function generates a schema summary report of a DataFrame and writes it to a text file.
def tbl_schema(dfrm):
    dfrm = pd.DataFrame(dfrm)
    buffer = io.StringIO()
    dfrm.info(buf=buffer, memory_usage='deep', verbose=True)
    schema = buffer.getvalue()
    f_name = updated_name_with_date('schema', 'txt')
    make_report(f_name, schema)
    pass

# This function generates a cardinality report (unique value counts) for each column in the DataFrame.
def tbl_cardin(dfrm):
    cardins = 'This is the cardinality report of table. \n\n'
    for col in dfrm.columns:
        cardin = (dfrm[col].value_counts()).to_string()
        cardin_msg = f'The cardinality of *{col}* is:\n'
        cardins = cardins + cardin_msg + cardin + '\n\n'
    print(cardins)
    f_name = updated_name_with_date('cardinality', 'txt')
    make_report(f_name, cardins)
    pass

# This function reads a CSV file, removes quotes from headers and values, and saves the cleaned version.
def remove_quotes(file_path, output_path):
    try:
        # Read CSV as strings (object type)
        df = pd.read_csv(file_path, dtype=str)

        # Remove quotes from column headers
        df.columns = [col.replace('"', '').replace("'", '') for col in df.columns]

        # Remove quotes from all data values (only if dtype is object)
        df = df.apply(lambda col: col.str.replace('"', '', regex=False).str.replace("'", '', regex=False)
                      if col.dtype == "object" else col)

        # Save cleaned DataFrame to new CSV
        df.to_csv(output_path, index=False)

        # Confirm the file was created
        if os.path.exists(output_path):
            print(f"✅ Cleaned CSV saved to: {output_path}")
        else:
            print(f"⚠️ CSV not saved. Check permissions or path: {output_path}")

        return df

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

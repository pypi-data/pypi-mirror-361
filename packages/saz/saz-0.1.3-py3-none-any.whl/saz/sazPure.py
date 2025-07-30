import os
from datetime import date
import pandas as pd

def updated_nm(initial, frmt):
    today = date.today()
    tdyfrmt = today.strftime('%Y%m%d')
    return f"{initial}_report_{tdyfrmt}.{frmt}"

def make_report(file_name, content):
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(content)

def remove_quotes(file_path, output_path):
    try:
        df = pd.read_csv(file_path, dtype=str)

        df.columns = [col.replace('"', '').replace("'", '') for col in df.columns]
        df = df.apply(lambda col: col.str.replace('"', '').str.replace("'", '') if col.dtype == "object" else col)

        df.to_csv(output_path, index=False)

        if os.path.exists(output_path):
            print(f"✅ Cleaned CSV saved to: {output_path}")
        else:
            print(f"⚠️ CSV not saved. Check permissions or path: {output_path}")

        return df
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
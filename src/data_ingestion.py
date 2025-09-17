import os
import pandas as pd

def ingest_excel(input_file: str, output_dir: str):
    print("🚀 Starting data ingestion...")

    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    xls = pd.ExcelFile(input_file, engine="openpyxl")
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, engine="openpyxl", header=0)
        file_name = sheet_name.lower().replace(" ", "_") + ".csv"
        output_path = os.path.join(output_dir, file_name)
        df.to_csv(output_path, index=False, encoding="utf-8")
        print(f"✅ Saved sheet '{sheet_name}' → {output_path}")

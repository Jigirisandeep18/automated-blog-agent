import pandas as pd
import gspread
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_gspread_client(creds_path="config/credentials.json"):
    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
    creds = flow.run_local_server(port=0)
    return gspread.authorize(creds)

def upload_metadata_to_sheet(metadata_csv_path="outputs/blogs_metadata.csv", sheet_name="Automated Blogs"):
    client = get_gspread_client()
    sheet = client.open(sheet_name).sheet1

    # Read metadata CSV
    df = pd.read_csv(metadata_csv_path)

    # Replace NaN with empty strings
    df = df.fillna("")

    # Append rows to Google Sheet
    for index, row in df.iterrows():
        sheet.append_row(row.tolist(), value_input_option="RAW")
        print(f"✅ Uploaded row #{index + 1} to Google Sheet.")

    print("🎉 All metadata uploaded successfully.")

if __name__ == "__main__":
    upload_metadata_to_sheet()

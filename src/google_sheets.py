import os
import json
import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

TOKEN_PATH = "config/token.json"

def get_client(creds_path="config/credentials.json"):
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for next runs
            with open(TOKEN_PATH, "w") as token_file:
                token_file.write(creds.to_json())

    return gspread.authorize(creds)


def append_blog(row_data, sheet_name="Automated Blogs", creds_path="config/credentials.json"):
    """
    Append a blog entry into Google Sheets.
    row_data: list in order:
    [Title, Meta Title, Meta Description, SEO Keywords, LLM Keywords, Deeplinks, Blog Content, FAQs, CTA]
    """
    client = get_client(creds_path)
    sheet = client.open(sheet_name).sheet1
    sheet.append_row(row_data, value_input_option="RAW")
    print(f"✅ Blog appended to Google Sheet: {sheet_name}")

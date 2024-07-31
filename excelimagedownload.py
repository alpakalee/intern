import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# Google API 설정
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=creds)
sheets_service = build('sheets', 'v4', credentials=creds)

SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'
SHEET_NAME = 'Tags'

def get_sheet_data():
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])
    if not values or len(values[0]) < 3:
        values = [['File ID', 'File Name', 'Tags']]
    for row in values[1:]:
        if len(row) < 3:
            row.append(None)
    return pd.DataFrame(values[1:], columns=values[0])

def search_files_by_tag(tag):
    df = get_sheet_data()
    result_files = df[df['Tags'].str.contains(tag, na=False)]
    return result_files['File Name'].tolist(), result_files['File ID'].tolist()

def download_file(file_id, file_name, dest_folder):
    request = drive_service.files().get_media(fileId=file_id)
    file_path = os.path.join(dest_folder, file_name)
    with open(file_path, 'wb') as f:
        f.write(request.execute())

def main():
    search_tag = input("Enter the tag to search for: ")
    dest_folder = input("Enter the destination folder path: ")
    
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    file_names, file_ids = search_files_by_tag(search_tag)
    if not file_names:
        print(f"No files found with tag '{search_tag}'")
        return

    for file_name, file_id in zip(file_names, file_ids):
        print(f"Downloading {file_name}...")
        download_file(file_id, file_name, dest_folder)
        print(f"Downloaded {file_name} to {dest_folder}")

if __name__ == "__main__":
    main()

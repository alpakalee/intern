import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

# OAuth 2.0 클라이언트 ID로 인증
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = ' '

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Google Drive API 클라이언트 생성
drive_service = build('drive', 'v3', credentials=creds)

# Google Sheets API 클라이언트 생성
sheets_service = build('sheets', 'v4', credentials=creds)

SPREADSHEET_ID = ' '  # 스프레드시트 ID
SHEET_NAME = 'Tags'

def get_sheet_data():
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])
    if not values:
        values = [['File ID', 'File Name', 'Tags']]
    return pd.DataFrame(values[1:], columns=values[0])

def update_sheet_data(df):
    sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_NAME,
        valueInputOption='RAW',
        body={'values': [df.columns.values.tolist()] + df.values.tolist()}
    ).execute()

def add_tag(file_id, tags):
    df = get_sheet_data()

    if file_id in df['File ID'].values:
        df.loc[df['File ID'] == file_id, 'Tags'] = df[df['File ID'] == file_id]['Tags'] + ', ' + ', '.join(tags)
    else:
        file_name = drive_service.files().get(fileId=file_id).execute()['name']
        new_row = {'File ID': file_id, 'File Name': file_name, 'Tags': ', '.join(tags)}
        df = df.append(new_row, ignore_index=True)

    update_sheet_data(df)

def search_by_tag(tag):
    df = get_sheet_data()

    result_files = df[df['Tags'].str.contains(tag, na=False)]
    if not result_files.empty:
        print("Files with tag '{}':\n".format(tag))
        for index, row in result_files.iterrows():
            print("File Name: {}, File ID: {}".format(row['File Name'], row['File ID']))
    else:
        print("No files found with tag '{}'".format(tag))

def show_all_tags():
    df = get_sheet_data()

    all_tags = set()
    for tags in df['Tags']:
        all_tags.update(tags.split(', '))
    
    print("All tags:\n" + ', '.join(all_tags))

# 예시 사용 방법
if __name__ == "__main__":
    # 파일에 태그 추가
    add_tag('파일_ID', ['태그1', '태그2'])

    # 태그로 파일 검색
    search_by_tag('태그1')

    # 모든 태그 보기
    show_all_tags()

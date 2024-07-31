from google.oauth2 import service_account
from googleapiclient.discovery import build

# OAuth 2.0 클라이언트 ID로 인증
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = ''

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Google Drive API 클라이언트 생성
drive_service = build('drive', 'v3', credentials=creds)

def get_file_id(file_name):
    results = drive_service.files().list(
        q=f"name='{file_name}'",
        fields="files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print(f'No files found with name: {file_name}')
        return None
    else:
        print(f"Found file: {items[0]['name']} with ID: {items[0]['id']}")
        return items[0]['id']

# 예시 사용 방법
file_name = ''
file_id = get_file_id(file_name)
print(f"The file ID for {file_name} is {file_id}")

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# Google API 설정
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # 여기에 실제 파일 경로를 넣으세요

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

drive_service = build('drive', 'v3', credentials=creds)
sheets_service = build('sheets', 'v4', credentials=creds)

SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'  # 여기에 실제 스프레드시트 ID를 넣으세요
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
    try:
        with open(file_path, 'wb') as f:
            f.write(request.execute())
    except Exception as e:
        print(f"Error downloading {file_name}: {e}")

def download_files(search_tag, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    file_names, file_ids = search_files_by_tag(search_tag)
    if not file_names:
        messagebox.showinfo("Info", f"No files found with tag '{search_tag}'")
        return

    for file_name, file_id in zip(file_names, file_ids):
        print(f"Downloading {file_name}...")
        download_file(file_id, file_name, dest_folder)
        print(f"Downloaded {file_name} to {dest_folder}")

    messagebox.showinfo("Info", f"Downloaded {len(file_names)} files to {dest_folder}")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Drive File Downloader")

        self.tag_label = tk.Label(root, text="Enter the tag to search for:")
        self.tag_label.pack(padx=10, pady=5)
        
        self.tag_entry = tk.Entry(root, width=50)
        self.tag_entry.pack(padx=10, pady=5)
        
        self.folder_label = tk.Label(root, text="Enter the destination folder path:")
        self.folder_label.pack(padx=10, pady=5)
        
        self.folder_entry = tk.Entry(root, width=50)
        self.folder_entry.pack(padx=10, pady=5)
        
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_folder)
        self.browse_button.pack(pady=5)

        self.download_button = tk.Button(root, text="Download", command=self.download)
        self.download_button.pack(pady=20)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def download(self):
        search_tag = self.tag_entry.get().replace('"', '').strip()
        dest_folder = self.folder_entry.get().replace('"', '').strip()
        
        if not search_tag:
            messagebox.showwarning("Warning", "Please enter a tag to search for.")
            return
        
        if not dest_folder:
            messagebox.showwarning("Warning", "Please enter or select a destination folder.")
            return
        
        download_files(search_tag, dest_folder)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

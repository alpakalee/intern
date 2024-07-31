import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
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

def update_sheet_data(df):
    sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=SHEET_NAME,
        valueInputOption='RAW',
        body={'values': [df.columns.values.tolist()] + df.values.tolist()}
    ).execute()

def get_drive_images():
    results = drive_service.files().list(
        q="mimeType contains 'image/'",
        fields="files(id, name, mimeType)").execute()
    return results.get('files', [])

def get_image_data(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    file_data = io.BytesIO(request.execute())
    return file_data

class ImageTaggerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Tagger")

        # Setup Frames
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        # Image Display
        self.image_label = tk.Label(self.left_frame)
        self.image_label.pack()

        # Tag Entry
        self.tag_entry_label = tk.Label(self.right_frame, text="Enter Tags:")
        self.tag_entry_label.pack()
        self.tag_entry = tk.Entry(self.right_frame, width=50)
        self.tag_entry.pack(pady=5)
        self.save_button = tk.Button(self.right_frame, text="Save Tags", command=self.save_tags)
        self.save_button.pack(pady=5)

        # Load initial images
        self.load_images()

    def load_images(self):
        self.df = get_sheet_data()
        self.images = get_drive_images()
        self.current_image_index = 0
        self.show_next_image()

    def show_next_image(self):
        while self.current_image_index < len(self.images):
            file = self.images[self.current_image_index]
            if file['id'] not in self.df['File ID'].values:
                image_data = get_image_data(file['id'])
                image = Image.open(image_data)
                image.thumbnail((400, 400))
                self.photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=self.photo)
                self.current_file = file
                self.tag_entry.delete(0, tk.END)
                return
            self.current_image_index += 1
        messagebox.showinfo("Info", "No more images to tag")

    def save_tags(self):
        tags = self.tag_entry.get()
        if tags:
            new_row = pd.DataFrame([{
                'File ID': self.current_file['id'],
                'File Name': self.current_file['name'],
                'Tags': tags
            }])
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            update_sheet_data(self.df)
            self.current_image_index += 1
            self.show_next_image()
        else:
            messagebox.showwarning("Warning", "Please enter tags before saving")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageTaggerApp(root)
    root.mainloop()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver import ChromeOptions
import time
import pyautogui
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pyperclip
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 좌표 설정
x_win = 897
y_win = 40
x_kakao = 1470
y_kakao = 146
x_chat = 1646
y_chat = 138

#설정 일 수
setting_date = 3

today = datetime.today().date()

def driversetup(url):
    options = ChromeOptions()
    options.add_argument("--headless")  # 백그라운드에서 실행
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)
    time.sleep(5)
    return driver

def send_to_kakao(messages):
    pyautogui.hotkey("winleft", "d")
    pyautogui.moveTo(x_win, y_win)
    pyautogui.doubleClick()
    time.sleep(15)
    pyautogui.moveTo(x_kakao, y_kakao)
    pyautogui.click()
    time.sleep(1)
    
    pyautogui.moveTo(x_chat, y_chat)
    pyautogui.doubleClick()
    time.sleep(3)
    
    pyperclip.copy(f"지난 {setting_date}일간의 알림")
    pyautogui.hotkey("ctrl", "v")
    pyautogui.hotkey("shift", "enter")
    time.sleep(1)
        
    for message in messages:
        pyperclip.copy(message)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.hotkey("shift", "enter")
        time.sleep(1)
    pyautogui.press('enter')
    time.sleep(1)
    pyautogui.press('esc')
    pyautogui.press('esc')

def sheetselect(spreadsheet_id, send_url, sheet_name, messages):
    count = 0
    # 구글 스프레드시트 인증
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(" ", scope)
    gc = gspread.authorize(creds)

    # 스프레드시트 열기
    doc = gc.open_by_key(spreadsheet_id)
    worksheet = doc.worksheet("설문지 응답 시트1")
    dates = worksheet.col_values(1)
    
    for date_str in dates:
        try:
            if (date_str == "타임스탬프"):
                continue
            date_only_str = date_str.split()[0] + " " + date_str.split()[1] + " " + date_str.split()[2]
            date_obj = datetime.strptime(date_only_str, '%Y. %m. %d').date()
            date_diff = abs((today - date_obj).days)

            if (date_diff <= setting_date):
                count += 1
            else:
                pass
        except ValueError as ve:
            print(f"유효하지 않은 날짜 형식: {date_str}, 오류: {ve}")
    
    if (count > 0):
        message = f"{sheet_name}에 {count}개의 새로운 응답이 있습니다. 링크: {send_url}"
        messages.append(message)

messages = []
# 돌/가족행사 시트
sheetselect(" ", " ", "돌/가족행사", messages)
# 웨딩 시트
sheetselect(" ", " ", "웨딩", messages)
# 비즈니스 시트
sheetselect(" ", " ", "비즈니스", messages)

# 카카오톡으로 메시지 전송
if messages:
    send_to_kakao(messages)

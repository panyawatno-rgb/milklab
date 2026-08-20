import os
import sys
import json
import argparse
from datetime import datetime
import gspread
import requests
from dotenv import load_dotenv

load_dotenv()

def send_telegram_notification(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"[warning] Telegram failed: {e}")

def log_sale(menu: str, qty: int, price: float):
    creds_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    sheet_id = os.getenv("SPREADSHEET_ID")
    
    if not creds_json or not sheet_id:
        print("[tool] error: Missing GOOGLE_SHEETS_CREDENTIALS or SPREADSHEET_ID")
        sys.exit(1)
        
    try:
        creds_dict = json.loads(creds_json)
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(sheet_id)
        worksheet = sh.sheet1
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = qty * price
        
        row = [timestamp, menu, qty, price, total]
        worksheet.append_row(row)
        
        msg = f"🔔 [Sales Alert]\nเมนู: {menu}\nจำนวน: {qty}\nราคา/ชิ้น: {price}\nรวม: {total} บาท"
        send_telegram_notification(msg)
        
        return f"OK: บันทึก {total:.0f} บาท notif via telegram"
        
    except Exception as e:
        print(f"[tool] error: {type(e).__name__}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--menu", type=str, required=True)
    parser.add_argument("--qty", type=int, required=True)
    parser.add_argument("--price", type=float, required=True)
    args = parser.parse_args()
    
    res = log_sale(args.menu, args.qty, args.price)
    print(res)
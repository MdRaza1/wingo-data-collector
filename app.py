import os, json, time, threading, requests, gspread
from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

def get_sheet():
    # यहाँ हम .strip() जोड़ रहे हैं ताकि कोई भी फालतू स्पेस या न्यू लाइन एरर न दे
    creds_json = os.environ.get('GOOGLE_CRED').strip()
    creds_dict = json.loads(creds_json)
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open('WingoData').sheet1

def collect_data():
    print("🚀 Background Collector Thread Started!")
    while True:
        try:
            sheet = get_sheet()
            response = requests.get("https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json", timeout=10)
            data = response.json()
            records = data.get("data", {}).get("list", [])
            
            existing_issues = {str(r["issueNumber"]) for r in sheet.get_all_records()}
            new_records = [r for r in reversed(records) if str(r["issueNumber"]) not in existing_issues]
            
            for r in new_records:
                sheet.append_row([r["issueNumber"], r["number"], r["color"]])
            
            if new_records: print(f"✅ Saved {len(new_records)} new rows.")
            else: print("⏳ No new data.")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(60)

@app.route('/')
def home():
    return "✅ WinGo Data Collector is running!"

if __name__ == '__main__':
    threading.Thread(target=collect_data, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
    

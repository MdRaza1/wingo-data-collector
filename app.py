from flask import Flask
import requests
import json
import time
import threading
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Google Sheet सेटअप
def get_sheet():
    # Render के Environment से क्रेडेंशियल उठाना
    creds_json = os.environ.get('GOOGLE_CRED') 
    creds_dict = json.loads(creds_json)
    
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # अपनी शीट का नाम 'WingoData' रखें
    return client.open('WingoData').sheet1

# डेटा कलेक्ट करने वाला इंजन
def collect_data():
    print("🚀 Background Collector Thread Started!")
    API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
    
    while True:
        try:
            sheet = get_sheet()
            response = requests.get(API_URL, timeout=10)
            data = response.json()
            records = data.get("data", {}).get("list", [])
            
            # शीट से पुराना डेटा लाएं
            existing_data = sheet.get_all_records()
            existing_issues = {str(r["issueNumber"]) for r in existing_data}
            
            # सिर्फ नया डेटा फिल्टर करें
            new_records = [r for r in records if str(r["issueNumber"]) not in existing_issues]
            
            if new_records:
                for r in reversed(new_records):
                    sheet.append_row([r["issueNumber"], r["number"], r["color"]])
                print(f"✅ Saved {len(new_records)} new rows.")
            else:
                print("⏳ No new data.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(60) # हर 60 सेकंड में चेक करेगा

@app.route('/')
def home():
    return "✅ WinGo Data Collector is running 24/7!"

if __name__ == '__main__':
    # बैकग्राउंड थ्रेड शुरू करें
    thread = threading.Thread(target=collect_data, daemon=True)
    thread.start()
    
    # Flask ऐप चलाएं
    app.run(host='0.0.0.0', port=8080)
    

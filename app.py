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
    # Render के Environment Variable से क्रेडेंशियल्स उठाना
    creds_json = os.environ.get('GOOGLE_CRED') 
    creds_dict = json.loads(creds_json)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open('WingoData').sheet1 # अपनी Google Sheet का नाम लिखें

@app.route('/')
def home():
    return "✅ WinGo Data Collector is Running with Google Sheets!"

def collect_data():
    API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
    sheet = get_sheet()
    
    while True:
        try:
            print("🔄 Fetching data...")
            response = requests.get(API_URL, timeout=10)
            data = response.json()
            records = data.get("data", {}).get("list", [])
            
            # शीट से पुराना डेटा लाओ (ताकि डुप्लीकेट न हो)
            existing_data = sheet.get_all_records()
            existing_issues = {str(r["issueNumber"]) for r in existing_data}
            
            new_records = [r for r in records if str(r["issueNumber"]) not in existing_issues]
            
            if new_records:
                for r in reversed(new_records):
                    # शीट में कॉलम के हिसाब से डेटा डालो
                    sheet.append_row([r["issueNumber"], r["number"], r["color"]])
                print(f"✅ Saved {len(new_records)} new rows.")
            else:
                print("⏳ No new data.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(60)

if __name__ == '__main__':
    thread = threading.Thread(target=collect_data, daemon=True)
    thread.start()
    app.run(host='0.0.0.0', port=8080)
    

from flask import Flask
import requests
import json
import time
import threading

app = Flask(__name__)

# ---- ये रूट Render को बताता है कि ऐप चालू है ----
@app.route('/')
def home():
    return "✅ WinGo Data Collector is Running 24/7!"

# ---- डेटा कलेक्ट करने वाला इंजन ----
def collect_data():
    API_URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
    FILE_NAME = "wingo_data.json"
    
    while True:
        try:
            print("🔄 Fetching data...")
            response = requests.get(API_URL, timeout=10)
            data = response.json()
            records = data.get("data", {}).get("list", [])
            
            if records:
                # पुराना डेटा लोड करो
                try:
                    with open(FILE_NAME, "r") as f:
                        existing = json.load(f)
                except:
                    existing = []
                
                # डुप्लिकेट हटाओ (issueNumber के हिसाब से)
                existing_issues = {r["issueNumber"] for r in existing}
                new_records = [r for r in records if r["issueNumber"] not in existing_issues]
                
                if new_records:
                    existing.extend(new_records)
                    with open(FILE_NAME, "w") as f:
                        json.dump(existing, f, indent=2)
                    print(f"✅ Saved {len(new_records)} new. Total: {len(existing)}")
                else:
                    print("⏳ No new data.")
            else:
                print("⚠️ No records found.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(60)  # हर 60 सेकंड में चलेगा

# ---- सबसे पहले यह फंक्शन चलेगा ----
if __name__ == '__main__':
    # कलेक्टर को बैकग्राउंड में चलाओ (ताकि वेबसाइट भी चले)
    thread = threading.Thread(target=collect_data, daemon=True)
    thread.start()
    # सर्वर शुरू करो (Render को यही चाहिए)
    app.run(host='0.0.0.0', port=8080)

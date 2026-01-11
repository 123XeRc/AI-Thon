
import httpx
import uuid
from datetime import datetime
import time

def test_api():
    base_url = "http://127.0.0.1:8000"
    print("Assuming API is running on port 8000...")
    
    # 1. Test Categorization
    payload = {
      "transaction_id": f"txn_{uuid.uuid4()}",
      "account_id": "acc_test",
      "account_name": "Test Acc",
      "transaction_date": datetime.now().isoformat(),
      "amount": 150.00,
      "currency": "INR",
      "transaction_type": "DEBIT",
      # Using a new merchant to test AI
      "beneficiary_name": "New Cafe Test", 
      "remarks": "Coffee",
      "mode": "UPI"
    }
    
    print("\n--- Testing POST /categorize ---")
    try:
        resp = httpx.post(f"{base_url}/categorize", json=payload, timeout=30)
        if resp.status_code == 200:
            print("Success:", resp.json())
        else:
            print("Error:", resp.text)
    except Exception as e:
        print("Failed to connect. Make sure server is running:", e)

    # 2. Test History
    print("\n--- Testing GET /transactions ---")
    try:
        resp = httpx.get(f"{base_url}/transactions?limit=3", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Fetched {len(data)} transactions")
            if data:
                print("First:", data)
        else:
            print("Error:", resp.text)
    except Exception as e:
        print("Failed to connect:", e)

if __name__ == "__main__":
    # Wait a bit if this script is auto-run after starting server
    time.sleep(2) 
    test_api()

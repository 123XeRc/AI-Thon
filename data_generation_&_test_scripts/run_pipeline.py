
from pipeline import TransactionPipeline
import uuid
from datetime import datetime

def main():
    pipeline = TransactionPipeline()
    
    # 1. Sample from Prompt (Normalized Clean/MCC hit likely)
    payload_1 = {
      "transaction_id": f"txn_{uuid.uuid4()}",
      "account_id": "acc_001",
      "account_name": "Salary Account",
      "transaction_date": datetime.now().isoformat(),
      "amount": 2499.00,
      "currency": "INR",
      "transaction_type": "DEBIT",
      "beneficiary_name": "Amazon Seller Services",
      "remarks": "AMZN MKTPLACE PMTS",
      "merchant_name": "Amazon",
      "mcc": "5311",
      "mode": "CARD",
    }

    print("\n--- TEST 1: Amazon (MCC/Merchant) ---")
    res1 = pipeline.categorize(payload_1)
    print(res1)
    
    # 2. Sample Charity (AI Fallback or Embedding)
    payload_2 = {
      "transaction_id": f"txn_{uuid.uuid4()}",
      "account_id": "acc_001",
      "account_name": "Salary Account",
      "transaction_date": datetime.now().isoformat(),
      "amount": 500.00,
      "currency": "INR",
      "transaction_type": "DEBIT",
      "beneficiary_name": "Sitaram Temple",
      "remarks": "Payment",
      "merchant_name": None,
      "mcc": None,
      "mode": "UPI",
    }

    
    print("\n--- TEST 2: Temple Donation (Semantic/AI) ---")
    res2 = pipeline.categorize(payload_2)
    print(res2)

    # 2. Sample Unknown (AI Fallback or Embedding)
    payload_2 = {
      "transaction_id": f"txn_{uuid.uuid4()}",
      "account_id": "acc_002",
      "account_name": "Savings Account",
      "transaction_date": datetime.now().isoformat(),
      "amount": 500.00,
      "currency": "INR",
      "transaction_type": "DEBIT",
      "beneficiary_name": "Amazon Services",
      "remarks": "Payment",
      "merchant_name": None,
      "mcc": None,
      "mode": "UPI",
    }

    # 3. Repeat Sample Charity to test Learning Loop
    print("\n--- TEST 3: Temple Donation REPEAT (Should be Learned) ---")
    # Using same beneficiary to trigger memory hit or embedding match
    payload_3 = payload_2.copy()
    payload_3["transaction_id"] = f"txn_{uuid.uuid4()}"
    
    res3 = pipeline.categorize(payload_3)
    print(res3)

    pipeline.close()

if __name__ == "__main__":
    main()

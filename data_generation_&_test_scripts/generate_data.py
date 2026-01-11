
import json
import random
import uuid
from datetime import datetime, timedelta

# --- CONSTANTS & CONFIG ---
OUTPUT_DIR = "data"
NUM_TRANSACTIONS = 2000
NUM_FEEDBACK = 200

# --- DATA DEFINITIONS ---

CATEGORIES = [
    {"category_id": 1, "category_name": "Income", "description": "Salary, refunds, cashback, and other credits"},
    {"category_id": 2, "category_name": "Food & Dining", "description": "Restaurants, cafes, food delivery"},
    {"category_id": 3, "category_name": "Groceries", "description": "Supermarkets, local grocery stores"},
    {"category_id": 4, "category_name": "Travel & Transport", "description": "Flights, trains, cabs, fuel, tolls"},
    {"category_id": 5, "category_name": "Utilities", "description": "Electricity, water, gas, internet, mobile bills"},
    {"category_id": 6, "category_name": "Shopping", "description": "Clothing, electronics, e-commerce, department stores"},
    {"category_id": 7, "category_name": "Health & Wellness", "description": "Pharmacies, hospitals, gyms, checkups"},
    {"category_id": 8, "category_name": "Entertainment", "description": "Movies, streaming services, events, gaming"},
    {"category_id": 9, "category_name": "Transfers", "description": "P2P transfers, wallet top-ups, family support"},
    {"category_id": 10, "category_name": "Investment", "description": "Stocks, mutual funds, gold, crypto, savings"},
    {"category_id": 11, "category_name": "Education", "description": "School fees, courses, books, tuition"},
    {"category_id": 12, "category_name": "Pets", "description": "Pet food, vet visits, grooming"},
    {"category_id": 13, "category_name": "Home Services", "description": "Repairs, cleaning, decor, furniture"},
    {"category_id": 14, "category_name": "Charity", "description": "Donations, NGOs, religious contributions"},
    {"category_id": 15, "category_name": "Insurance", "description": "Life, health, car, home insurance premiums"},
    {"category_id": 16, "category_name": "Taxes", "description": "Income tax, property tax, GST payments"},
    {"category_id": 17, "category_name": "Office & Business", "description": "Co-working, software subscriptions, office supplies"},
    {"category_id": 18, "category_name": "Gifts & Donations", "description": "Personal gifts, wedding envelopes"},
    {"category_id": 19, "category_name": "Kids", "description": "Toys, baby products, allowances"},
    {"category_id": 20, "category_name": "Personal Care", "description": "Salon, spa, cosmetics, grooming products"},
]

MCC_MAP = [
    # Food
    {"mcc": "5812", "category_name": "Food & Dining", "mcc_description": "Eating places and Restaurants"},
    {"mcc": "5814", "category_name": "Food & Dining", "mcc_description": "Fast Food Restaurants"},
    {"mcc": "5462", "category_name": "Food & Dining", "mcc_description": "Bakeries"},
    # Groceries
    {"mcc": "5411", "category_name": "Groceries", "mcc_description": "Grocery Stores, Supermarkets"},
    {"mcc": "5422", "category_name": "Groceries", "mcc_description": "Freezer and Locker Meat Provisioners"},
    # Travel
    {"mcc": "4121", "category_name": "Travel & Transport", "mcc_description": "Taxicabs and Limousines"},
    {"mcc": "5541", "category_name": "Travel & Transport", "mcc_description": "Service Stations and Automated Fuel Dispensers"},
    {"mcc": "4789", "category_name": "Travel & Transport", "mcc_description": "Transportation Services, Not Elsewhere Classified"},
    {"mcc": "4511", "category_name": "Travel & Transport", "mcc_description": "Airlines and Air Carriers"},
    # Utilities
    {"mcc": "4814", "category_name": "Utilities", "mcc_description": "Telecommunication Services"},
    {"mcc": "4900", "category_name": "Utilities", "mcc_description": "Electric, Gas, Sanitary and Water Utilities"},
    # Health
    {"mcc": "5912", "category_name": "Health & Wellness", "mcc_description": "Drug Stores and Pharmacies"},
    {"mcc": "8011", "category_name": "Health & Wellness", "mcc_description": "Doctors and Physicians"},
    {"mcc": "7991", "category_name": "Health & Wellness", "mcc_description": "Tourist Attractions and Exhibits (Gyms often miscategorized here or 7997)"},
    # Entertainment
    {"mcc": "7832", "category_name": "Entertainment", "mcc_description": "Motion Picture Theaters"},
    {"mcc": "5816", "category_name": "Entertainment", "mcc_description": "Digital Goods: Games"},
    # Shopping
    {"mcc": "5311", "category_name": "Shopping", "mcc_description": "Department Stores"},
    {"mcc": "5732", "category_name": "Shopping", "mcc_description": "Electronics Stores"},
    # Education
    {"mcc": "8211", "category_name": "Education", "mcc_description": "Elementary and Secondary Schools"},
    {"mcc": "8299", "category_name": "Education", "mcc_description": "Schools and Educational Services NEC"},
    # Pets
    {"mcc": "5995", "category_name": "Pets", "mcc_description": "Pet Shops, Pet Fruits, and Supplies"},
    {"mcc": "0742", "category_name": "Pets", "mcc_description": "Veterinary Services"},
    # Insurance
    {"mcc": "6300", "category_name": "Insurance", "mcc_description": "Insurance Sales, Underwriting, and Premiums"},
    # Financial
    {"mcc": "6011", "category_name": "Transfers", "mcc_description": "Financial Institutions – Automated Cash Disbursements"},
    {"mcc": "6211", "category_name": "Investment", "mcc_description": "Security Brokers/Dealers"},
]

MERCHANTS = [
    # Food
    {"name": "Starbucks", "category": "Food & Dining", "mcc": "5812"},
    {"name": "McDonalds", "category": "Food & Dining", "mcc": "5814"},
    {"name": "Zomato", "category": "Food & Dining", "mcc": "5812"},
    {"name": "Swiggy", "category": "Food & Dining", "mcc": "5812"},
    {"name": "Dominos", "category": "Food & Dining", "mcc": "5814"},
    {"name": "Subway", "category": "Food & Dining", "mcc": "5814"},
    # Groceries
    {"name": "Whole Foods", "category": "Groceries", "mcc": "5411"},
    {"name": "BigBasket", "category": "Groceries", "mcc": "5411"},
    {"name": "Blinkit", "category": "Groceries", "mcc": "5411"},
    {"name": "7-Eleven", "category": "Groceries", "mcc": "5411"},
    {"name": "Trader Joes", "category": "Groceries", "mcc": "5411"},
    # Travel
    {"name": "Uber", "category": "Travel & Transport", "mcc": "4121"},
    {"name": "Ola Cabs", "category": "Travel & Transport", "mcc": "4121"},
    {"name": "Shell Station", "category": "Travel & Transport", "mcc": "5541"},
    {"name": "Indian Oil", "category": "Travel & Transport", "mcc": "5541"},
    {"name": "Makemytrip", "category": "Travel & Transport", "mcc": "4789"},
    {"name": "IRCTC", "category": "Travel & Transport", "mcc": "4112"},
    # Shopping
    {"name": "Amazon", "category": "Shopping", "mcc": "5311"},
    {"name": "Flipkart", "category": "Shopping", "mcc": "5311"},
    {"name": "Myntra", "category": "Shopping", "mcc": "5691"},
    {"name": "Zara", "category": "Shopping", "mcc": "5621"},
    {"name": "Apple Store", "category": "Shopping", "mcc": "5732"},
    {"name": "IKEA", "category": "Home Services", "mcc": "5712"},
    # Entertainment
    {"name": "Netflix", "category": "Entertainment", "mcc": "5816"},
    {"name": "Spotify", "category": "Entertainment", "mcc": "5815"},
    {"name": "PVR Cinemas", "category": "Entertainment", "mcc": "7832"},
    {"name": "BookMyShow", "category": "Entertainment", "mcc": "7832"},
    {"name": "Steam Games", "category": "Entertainment", "mcc": "5816"},
    # Health
    {"name": "Apollo Pharmacy", "category": "Health & Wellness", "mcc": "5912"},
    {"name": "Cult Fit", "category": "Health & Wellness", "mcc": "7997"},
    {"name": "Practo", "category": "Health & Wellness", "mcc": "8011"},
    # Utilities
    {"name": "Jio Fiber", "category": "Utilities", "mcc": "4814"},
    {"name": "Airtel", "category": "Utilities", "mcc": "4814"},
    {"name": "BESCOM", "category": "Utilities", "mcc": "4900"},
    # Education
    {"name": "Udemy", "category": "Education", "mcc": "8299"},
    {"name": "Coursera", "category": "Education", "mcc": "8299"},
    {"name": "Byjus", "category": "Education", "mcc": "8299"},
    # Pets
    {"name": "Heads Up For Tails", "category": "Pets", "mcc": "5995"},
    {"name": "Drools", "category": "Pets", "mcc": "5995"},
    # Insurance
    {"name": "LIC India", "category": "Insurance", "mcc": "6300"},
    {"name": "PolicyBazaar", "category": "Insurance", "mcc": "6300"},
    # Investment
    {"name": "Zerodha", "category": "Investment", "mcc": "6211"},
    {"name": "CoinSwitch", "category": "Investment", "mcc": "6211"},
    # Office
    {"name": "WeWork", "category": "Office & Business", "mcc": "6513"},
    {"name": "Zoom Video", "category": "Office & Business", "mcc": "4816"},
]

MODES = ["UPI", "CARD", "NETBANKING", "NEFT"]
CURRENCY = "INR"

# --- GENERATION FUNCTIONS ---

def generate_merchant_memory():
    memory = []
    for m in MERCHANTS:
        memory.append({
            "merchant_key": m["name"].lower().replace(" ", ""),
            "merchant_display_name": m["name"],
            "category_name": m["category"],
            "confidence": round(random.uniform(0.90, 0.99), 4),
            "source": random.choice(["rule", "ai", "user_confirmed"]),
            "first_seen": (datetime.now() - timedelta(days=random.randint(100, 365))).isoformat(),
            "last_seen": (datetime.now() - timedelta(days=random.randint(0, 10))).isoformat(),
            "usage_count": random.randint(5, 500)
        })
    return memory

def generate_embedding_memory():
    patterns = [
        ("uber ride payment", "Travel & Transport"),
        ("netflix subscription", "Entertainment"),
        ("salary credit", "Income"),
        ("zomato order", "Food & Dining"),
        ("amazon purchase", "Shopping"),
        ("electricity bill payment", "Utilities"),
        ("gym membership fee", "Health & Wellness"),
        ("grocery shopping", "Groceries"),
        ("school fees payment", "Education"),
        ("pet food store", "Pets"),
        ("life insurance premium", "Insurance"),
        ("house rent", "Home Services"),
        ("charity donation", "Charity"),
        ("gift for friend", "Gifts & Donations"),
        ("tax payment", "Taxes"),
        ("office supplies", "Office & Business"),
        ("baby diapers", "Kids"),
        ("haircut salon", "Personal Care")
    ]
    memory = []
    for pattern, category in patterns:
        memory.append({
            "pattern_text": pattern,
            "category_name": category,
            "embedding": [], # Placeholder
            "usage_count": random.randint(1, 100),
            "first_seen": (datetime.now() - timedelta(days=random.randint(50, 200))).isoformat(),
            "last_seen": (datetime.now() - timedelta(days=random.randint(0, 20))).isoformat()
        })
    return memory

def generate_transactions(merchant_memory):
    transactions = []
    start_date = datetime.now() - timedelta(days=90) # Increased history
    
    for i in range(NUM_TRANSACTIONS):
        txn_type = "CREDIT" if random.random() < 0.15 else "DEBIT"
        date = start_date + timedelta(days=random.randint(0, 90), hours=random.randint(0, 23))
        
        # Base transaction
        txn = {
            "transaction_id": str(uuid.uuid4()),
            "account_id": "ACC_001",
            "account_name": "Primary Savings",
            "transaction_date": date.isoformat(),
            "amount": round(random.uniform(50, 200000) if txn_type == 'DEBIT' else random.uniform(1000, 150000), 2),
            "currency": CURRENCY,
            "transaction_type": txn_type,
            "mode": random.choice(MODES)
        }

        # Logic for fields based on type and simulated categorization source
        if txn_type == "CREDIT":
            if random.random() < 0.8:
                txn["beneficiary_name"] = "TechCorp Inc"
                txn["remarks"] = "Salary for Month"
                txn["clean_description"] = "salary credit"
                txn["category_name"] = "Income"
            else:
                txn["beneficiary_name"] = "Friend/Refund"
                txn["remarks"] = "Refund"
                txn["clean_description"] = "refund received"
                txn["category_name"] = "Income"
                
            txn["merchant_name"] = None
            txn["mcc"] = None
            txn["confidence"] = 1.0
            txn["source"] = "rule"
            txn["raw_description"] = "CREDIT TXN"
            
        else:
            # DEBIT Logic
            # Pick a scenario: Merchant Store, MCC Match, Embedding Match, or Unknown
            rand_val = random.random()
            
            if rand_val < 0.5: # Merchant Knowledge (High Confidence)
                merchant = random.choice(MERCHANTS)
                txn["merchant_name"] = merchant["name"]
                txn["mcc"] = merchant["mcc"]
                txn["beneficiary_name"] = merchant["name"].upper() + " MERCH"
                txn["remarks"] = f"Purchase at {merchant['name']}"
                txn["raw_description"] = f"POS - {merchant['name']} - {txn['mcc']}"
                txn["clean_description"] = merchant["name"].lower()
                txn["category_name"] = merchant["category"]
                txn["confidence"] = round(random.uniform(0.90, 0.99), 2)
                txn["source"] = "merchant_memory"

            elif rand_val < 0.75: # MCC Mapping (High Confidence)
                mcc_ref = random.choice(MCC_MAP)
                txn["merchant_name"] = "Unknown Store"
                txn["mcc"] = mcc_ref["mcc"]
                txn["beneficiary_name"] = f"STORE {random.randint(100,999)}"
                txn["remarks"] = "Card Payment"
                txn["raw_description"] = f"Txn / {mcc_ref['mcc']} / Store"
                txn["clean_description"] = f"transaction at store {mcc_ref['mcc']}"
                txn["category_name"] = mcc_ref["category_name"]
                txn["confidence"] = 0.95
                txn["source"] = "mcc"
            
            elif rand_val < 0.9: # Embedding/AI (Medium-High)
                # Cases where we infer from remarks/description
                patterns = [
                    ("gym subscription", "Health & Wellness"),
                    ("school bus fee", "Education"),
                    ("mobile recharge", "Utilities"),
                    ("dog food", "Pets"),
                    ("temple donation", "Charity"),
                    ("house maid salary", "Home Services"),
                    ("birthday gift", "Gifts & Donations")
                ]
                pat, cat = random.choice(patterns)
                
                txn["merchant_name"] = None
                txn["mcc"] = str(random.randint(1000, 9999))
                txn["beneficiary_name"] = "UPI USER"
                txn["remarks"] = pat
                txn["raw_description"] = f"UPI-{random.randint(100000,999999)}-{pat}"
                txn["clean_description"] = pat
                txn["category_name"] = cat
                txn["confidence"] = round(random.uniform(0.75, 0.89), 2)
                txn["source"] = "embedding_memory"
                
            else: # Low confidence / Fallback
                txn["merchant_name"] = None
                txn["mcc"] = None
                txn["beneficiary_name"] = "UNKNOWN BENEFICIARY"
                txn["remarks"] = "Payment"
                txn["raw_description"] = "UPI-123456-Unknown"
                txn["clean_description"] = "upi payment unknown"
                txn["category_name"] = "Transfers" # Default fallback
                txn["confidence"] = round(random.uniform(0.50, 0.70), 2)
                txn["source"] = "ai"

        transactions.append(txn)
    
    return transactions

def generate_feedback(transactions):
    feedback = []
    candidates = [t for t in transactions if t["category_name"] != "Income"]
    
    # Generate more feedback
    count = min(NUM_FEEDBACK, len(candidates))
    sample = random.sample(candidates, count)
        
    for txn in sample:
        possible_cats = [c["category_name"] for c in CATEGORIES if c["category_name"] != txn["category_name"]]
        new_cat = random.choice(possible_cats)
        
        feedback.append({
            "transaction_id": txn["transaction_id"],
            "old_category": txn["category_name"],
            "new_category": new_cat,
            "updated_by": "user",
            "updated_at": datetime.now().isoformat()
        })
    return feedback

# --- MAIN ---

def main():
    print(f"Generating expanded data in {OUTPUT_DIR}/...")
    
    # 1. Categories
    with open(f"{OUTPUT_DIR}/categories.json", "w") as f:
        json.dump(CATEGORIES, f, indent=2)
    
    # 2. MCC Map
    with open(f"{OUTPUT_DIR}/mcc_category_map.json", "w") as f:
        json.dump(MCC_MAP, f, indent=2)
        
    # 3. Merchant Memory
    merch_mem = generate_merchant_memory()
    with open(f"{OUTPUT_DIR}/merchant_category_memory.json", "w") as f:
        json.dump(merch_mem, f, indent=2)
        
    # 5. Embedding Memory
    emb_mem = generate_embedding_memory()
    with open(f"{OUTPUT_DIR}/embedding_memory.json", "w") as f:
        json.dump(emb_mem, f, indent=2)

    # 4. Transactions
    txns = generate_transactions(merch_mem)
    with open(f"{OUTPUT_DIR}/transactions.json", "w") as f:
        json.dump(txns, f, indent=2)

    # 6. Feedback
    fb = generate_feedback(txns)
    with open(f"{OUTPUT_DIR}/transaction_feedback.json", "w") as f:
        json.dump(fb, f, indent=2)
        
    print(f"Done. Generated {len(txns)} transactions and {len(CATEGORIES)} categories.")

if __name__ == "__main__":
    main()

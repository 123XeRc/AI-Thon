# Antigravity Prompt: Transaction Categorization Pipeline

You are a **fintech system architect and backend engineer**.

Your task is to **design and implement a transaction categorization pipeline**
for a **real-time Transaction Categorization Engine** using **historical data, rule-based memory, embeddings, and Azure OpenAI**.

The system must be **deterministic first** and **AI-assisted only as a fallback**.

---

## OVERALL GOAL 

Given a **single real-time transaction payload**, classify it into **one predefined category** using the following priority:

1. CREDIT rule
2. MCC mapping
3. Merchant memory (exact match)
4. Embedding memory (semantic similarity using Azure embeddings)
5. AI fallback using Azure OpenAI GPT-4o-mini (restricted to predefined categories)

---

## AVAILABLE DATA SOURCES (ALREADY STORED)

### SQL Tables
- categories
- mcc_category_map
- merchant_category_memory
- transactions
- embedding_memory

### Azure Services
- Azure OpenAI Embedding Model: text-embedding-3-large
- Azure OpenAI LLM Model: gpt-4o-mini

---

## INPUT (REAL-TIME TRANSACTION PAYLOAD)

Each incoming transaction contains:

{
  "transaction_id": "txn_123",
  "account_id": "acc_001",
  "account_name": "Salary Account",
  "transaction_date": "2024-02-15T12:34:00Z",
  "amount": 2499.00,
  "currency": "INR",
  "transaction_type": "DEBIT",
  "beneficiary_name": "Amazon Seller Services",
  "remarks": "AMZN MKTPLACE PMTS",
  "merchant_name": "Amazon",
  "mcc": "5311",
  "mode": "CARD",
  "raw_description": "AMZN MKTPLACE PMTS 14FEB"
}

---

## PIPELINE STEPS (STRICT ORDER)

### STEP 1: Normalize Transaction Text
- Generate clean_description
- Lowercase
- Remove dates, reference numbers, symbols
- Example:
  - "AMZN MKTPLACE PMTS 14FEB"
  - -> "amazon marketplace payment"

---

### STEP 2: CREDIT RULE
- If transaction_type == CREDIT
- Assign:
  - category_name = Income
  - source = rule
  - confidence = 0.99
- STOP PIPELINE

---

### STEP 3: MCC LOOKUP
- If mcc is present:
- Lookup mcc_category_map
- If match found:
  - Assign category
  - source = mcc
  - confidence >= 0.95
- STOP PIPELINE

---

### STEP 4: MERCHANT MEMORY (EXACT MATCH)
- Create merchant_key from:
  - merchant_name OR beneficiary_name
- Normalize:
  - lowercase, remove spaces and symbols
- Lookup merchant_category_memory
- If match found:
  - Assign stored category
  - Update:
    - usage_count += 1
    - last_seen = now()
  - source = merchant_memory
  - confidence >= 0.90
- STOP PIPELINE

---

### STEP 5: EMBEDDING MEMORY (SEMANTIC MATCH)
- Generate embedding using Azure text-embedding-3-large for clean_description
- Compare with embeddings in embedding_memory using cosine similarity
- If similarity >= threshold (e.g. 0.85):
  - Assign matched category
  - Update:
    - usage_count += 1
    - last_seen = now()
  - source = embedding_memory
  - confidence = similarity score
- STOP PIPELINE

---

### STEP 6: AI FALLBACK (LAST RESORT)
- Call Azure OpenAI gpt-4o-mini
- Provide:
  - clean_description
  - amount
  - mode
  - ONLY the predefined category list from categories table
- The model must:
  - Choose exactly one category
  - NOT invent new categories
- Output format:
{
  "category_name": "...",
  "confidence": 0.75-0.95
}
- Set:
  - source = ai

---

### STEP 7: POST-PROCESSING & LEARNING
- Insert classified transaction into transactions
- Update or insert:
  - merchant_category_memory (if merchant is new)
  - embedding_memory (store embedding for reuse)
- Ensure future transactions skip AI

---

## OUTPUT (FINAL CLASSIFICATION RESULT)

{
  "transaction_id": "txn_123",
  "clean_description": "amazon marketplace payment",
  "category_name": "Shopping",
  "confidence": 0.96,
  "source": "mcc"
}

---

## NON-FUNCTIONAL REQUIREMENTS

- AI must be called only if all memory layers fail
- Category must always come from categories table
- System must be explainable (source + confidence)
- Designed for high throughput and low latency
- Embeddings must be reused; avoid duplicates
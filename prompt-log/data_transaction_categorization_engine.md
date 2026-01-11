# Antigravity Prompt: Real-Time Transaction Categorization Data Generator

You are a **fintech data generator**.  
Your goal is to generate realistic **production-ready data** for a **real-time Transaction Categorization Engine**, and the output should be **ready to store in SQL**.

## USE CASE

- Transactions arrive in **real time** (CREDIT and DEBIT).  
- Each transaction contains raw details: beneficiary, remarks, amount, mode, and sometimes MCC.  
- Categorization follows this priority:
  1. **CREDIT → Income** (default)  
  2. **MCC mapping → assign category**  
  3. **Merchant memory → exact match**  
  4. **Embedding memory → semantic similarity**  
  5. **AI fallback → restricted to predefined categories**  
- User feedback updates **both transaction history and merchant memory**.

## DATA TO GENERATE

### 1️. Category Master Data (`categories`)
- predefined categories  
- Each record:
  - `category_id`  
  - `category_name`  
  - `description`

### 2️. MCC → Category Mapping (`mcc_category_map`)
- realistic MCC codes  
- Each record:
  - `mcc` (4-digit string)  
  - `category_name`  
  - `mcc_description`

### 3️. Merchant Memory (`merchant_category_memory`)
- One row per known merchant  
- Each record:
  - `merchant_key` (normalized lowercase)  
  - `merchant_display_name`  
  - `category_name`  
  - `confidence` (0.90–0.99)  
  - `source` (`rule`, `ai`, `user_confirmed`)  
  - `first_seen`  
  - `last_seen`  
  - `usage_count`

### 4️. Transaction History (`transactions`)
- Generate **realistic transactions**  
- Each record:
  - `transaction_id`  
  - `account_id`  
  - `account_name`  
  - `transaction_date`  
  - `amount`  
  - `currency`  
  - `transaction_type` (`CREDIT` / `DEBIT`)  
  - `beneficiary_name`  
  - `remarks`  
  - `merchant_name` (nullable)  
  - `mcc` (nullable)  
  - `mode` (`UPI`, `CARD`, `NETBANKING`, `NEFT`)  
  - `raw_description`  
  - `clean_description`  
  - `category_name`  
  - `confidence`  
  - `source` (`mcc`, `merchant_memory`, `embedding_memory`, `ai`, `rule`)

### 5️. Embedding Memory (`embedding_memory`)
- Each record:
  - `pattern_text` (cleaned description)  
  - `category_name`  
  - `embedding` (leave empty / placeholder for now)  
  - `usage_count`  
  - `first_seen`  
  - `last_seen`

### 6️. User Feedback (`transaction_feedback`) [Optional]
- 50 feedback records:  
  - `transaction_id`  
  - `old_category`  
  - `new_category`  
  - `updated_by`  
  - `updated_at`

## RULES

- Categories must come from predefined list  
- CREDIT → mostly Income  
- MCC → confidence ≥ 0.95  
- Merchant memory → confidence ≥ 0.90  
- Embedding memory → confidence 0.85–0.95  
- AI fallback → confidence 0.75–0.95  
- All data consistent and realistic

## OUTPUT

1. **Generate separate JSON files for each table**:  
   - `categories.json`  
   - `mcc_category_map.json`  
   - `merchant_category_memory.json`  
   - `transactions.json`  
   - `embedding_memory.json`  
   - `transaction_feedback.json`

2. **Or, optionally, generate one table at a time** (if needed for incremental scripts).  

3. **Also generate SQL scripts** to create tables and insert data.  

4. **Also generate Python scripts** to:
- Load JSON files  
- Insert into SQL  
- Generate embeddings for `embedding_memory` using Azure `text-embedding-3-large`  
- Store embeddings back in SQL (as JSON array or vector type depending on database)
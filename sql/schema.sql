
-- Categories Table
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- MCC Mapping Table
CREATE TABLE mcc_category_map (
    mcc TEXT PRIMARY KEY,
    category_name TEXT NOT NULL,
    mcc_description TEXT,
    FOREIGN KEY (category_name) REFERENCES categories(category_name)
);

-- Merchant Memory Table
CREATE TABLE merchant_category_memory (
    merchant_key TEXT PRIMARY KEY,
    merchant_display_name TEXT,
    category_name TEXT NOT NULL,
    confidence REAL,
    source TEXT,
    first_seen TEXT,
    last_seen TEXT,
    usage_count INTEGER,
    FOREIGN KEY (category_name) REFERENCES categories(category_name)
);

-- Transactions Table
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    account_id TEXT,
    account_name TEXT,
    transaction_date TEXT,
    amount REAL,
    currency TEXT,
    transaction_type TEXT, -- CREDIT / DEBIT
    beneficiary_name TEXT,
    remarks TEXT,
    merchant_name TEXT,
    mcc TEXT,
    mode TEXT,
    raw_description TEXT,
    clean_description TEXT,
    category_name TEXT,
    confidence REAL,
    source TEXT,
    FOREIGN KEY (category_name) REFERENCES categories(category_name)
);

-- Embedding Memory Table
CREATE TABLE embedding_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_text TEXT NOT NULL,
    category_name TEXT NOT NULL,
    embedding TEXT, -- JSON string or vector if supported
    usage_count INTEGER,
    first_seen TEXT,
    last_seen TEXT,
    FOREIGN KEY (category_name) REFERENCES categories(category_name)
);

-- Feedback Table
CREATE TABLE transaction_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT NOT NULL,
    old_category TEXT,
    new_category TEXT,
    updated_by TEXT,
    updated_at TEXT,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);

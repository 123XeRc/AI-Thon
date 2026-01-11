
import json
import sqlite3
import os
import time
from typing import List, Dict, Any

# Try importing openai, handle if not installed
try:
    from openai import AzureOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: 'openai' package not found. Embedding generation will be skipped or mocked.")

# --- CONFIG ---
DB_FILE = "transactions.db"
DATA_DIR = "data"
SQL_FILE = "sql/schema.sql"

# Azure Config (Replace with env vars or actual keys in production)
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = "2023-05-15"
DEPLOYMENT_NAME = "text-embedding-3-large"

# --- DATABASE FUNCTIONS ---

def init_db():
    """Initialize the database with the schema."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    with open(SQL_FILE, 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
        
    conn.commit()
    print("Database initialized.")
    return conn

def load_json(filename):
    with open(os.path.join(DATA_DIR, filename), 'r') as f:
        return json.load(f)

def insert_data(conn, table, data):
    """Generic insert function for list of dicts."""
    if not data:
        return
    
    keys = data[0].keys()
    columns = ', '.join(keys)
    placeholders = ', '.join(['?'] * len(keys))
    sql = f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})"
    
    values = []
    for row in data:
        values.append([str(row.get(k)) if isinstance(row.get(k), (dict, list)) else row.get(k) for k in keys])
        
    cursor = conn.cursor()
    cursor.executemany(sql, values)
    conn.commit()
    print(f"Inserted {len(data)} rows into {table}.")

# --- EMBEDDING FUNCTIONS ---

def get_azure_embedding(client, text):
    """Calls Azure OpenAI to get embedding."""
    try:
        response = client.embeddings.create(
            input=text,
            model=DEPLOYMENT_NAME
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding for '{text}': {e}")
        return None

def process_embeddings(conn):
    """Updates embedding_memory table with actual embeddings."""
    if not OPENAI_AVAILABLE:
        print("Skipping embedding generation (openai lib missing).")
        return

    if "your-key" in AZURE_API_KEY:
        print("Skipping embedding generation (API Key not configured).")
        return

    client = AzureOpenAI(
        api_key=AZURE_API_KEY,
        api_version=API_VERSION,
        azure_endpoint=AZURE_ENDPOINT
    )

    cursor = conn.cursor()
    cursor.execute("SELECT id, pattern_text FROM embedding_memory WHERE embedding IS NULL OR embedding = '[]'")
    rows = cursor.fetchall()
    
    print(f"Generating embeddings for {len(rows)} patterns...")
    
    for row_id, text in rows:
        embedding = get_azure_embedding(client, text)
        if embedding:
            # Store as JSON string for SQLite
            emb_str = json.dumps(embedding)
            cursor.execute("UPDATE embedding_memory SET embedding = ? WHERE id = ?", (emb_str, row_id))
            print(f"Generated embedding for: {text}")
            time.sleep(0.1) # Rate limit precaution
            
    conn.commit()
    print("Embedding generation complete.")

# --- MAIN ---

def main():
    if not os.path.exists(DATA_DIR):
        print(f"Data directory '{DATA_DIR}' not found. Run generate_data.py first.")
        return

    conn = init_db()
    
    # Load and Insert
    try:
        categories = load_json("categories.json")
        insert_data(conn, "categories", categories)
        
        mcc_map = load_json("mcc_category_map.json")
        insert_data(conn, "mcc_category_map", mcc_map)
        
        merch_mem = load_json("merchant_category_memory.json")
        insert_data(conn, "merchant_category_memory", merch_mem)
        
        txns = load_json("transactions.json")
        insert_data(conn, "transactions", txns)
        
        emb_mem = load_json("embedding_memory.json")
        insert_data(conn, "embedding_memory", emb_mem)
        
        feedback = load_json("transaction_feedback.json")
        insert_data(conn, "transaction_feedback", feedback)
        
        # Post-process embeddings
        process_embeddings(conn)
        
        print("\nSUCCESS: Data loaded into transactions.db")
        
        # Validation query
        cursor = conn.cursor()
        cursor.execute("SELECT category_name, COUNT(*) FROM transactions GROUP BY category_name")
        print("\nTransaction Summary:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
            
    except Exception as e:
        print(f"Error calling load logic: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()


import sqlite3
import json
import re
import numpy as np
from datetime import datetime
from config.config import *
from src.adapters.azure_openai import AsyncAzureOpenAIHelper
import asyncio

DB_FILE = os.path.join(os.getcwd(), "database", "transactions.db")

# Initialize OpenAI Client
try:
    client = AsyncAzureOpenAIHelper()
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("WARNING: OpenAI SDK not installed. AI steps will fail.")

class TransactionPipeline:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.categories = self._load_categories()
        # Cache MCC map for speed (Layer 2)
        self.mcc_map = self._load_mcc_map()
        
    def _load_categories(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT category_name FROM categories")
        return [row[0] for row in cursor.fetchall()]

    def _load_mcc_map(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT mcc, category_name FROM mcc_category_map")
        return {row[0]: row[1] for row in cursor.fetchall()}

    def normalize_text(self, text):
        """Step 1: Normalize Transaction Text"""
        if not text:
            return ""
        # Lowercase
        text = text.lower()
        # Remove dates (simple regex for DDMon or DD/MM)
        text = re.sub(r'\d{1,2}[a-z]{3}', '', text) 
        # Remove reference numbers (longer sequences of digits)
        text = re.sub(r'\b\d{4,}\b', '', text)
        # Remove special chars
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        # Collapse whitespace
        return ' '.join(text.split())

    def get_embedding(self, text):
        if not OPENAI_AVAILABLE or not text:
            return None
        try:
            response = asyncio.run(client.generate_embeddings(text))
            return response
        except Exception as e:
            print(f"Embedding Error: {e}")
            return None

    def cosine_similarity(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def categorize(self, txn_payload):
        """
        Main Pipeline Entry Point
        """
        txn_id = txn_payload.get("transaction_id")
        raw_desc = txn_payload.get("raw_description", "")
        amount = txn_payload.get("amount")
        mode = txn_payload.get("mode")
        
        # --- Step 1: Normalize ---
        # User Feedback: Real inputs lack explicit description. Construct from available fields.
        raw_desc = txn_payload.get("raw_description", "")
        if not raw_desc:
            parts = [
                txn_payload.get("beneficiary_name") or "",
                txn_payload.get("remarks") or ""
            ]
            raw_desc = " ".join([p for p in parts if p])

        clean_desc = self.normalize_text(raw_desc)
        print(f"Processing '{txn_id}': Clean Desc: '{clean_desc}'")

        result = {
            "transaction_id": txn_id,
            "clean_description": clean_desc,
            "category_name": None,
            "confidence": 0.0,
            "source": None
        }

        # --- Step 2: CREDIT RULE ---
        if txn_payload.get("transaction_type") == "CREDIT":
            result["category_name"] = "Income"
            result["confidence"] = 0.99
            result["source"] = "rule"
            self._finalize(result, txn_payload)
            return result

        # --- Step 3: MCC LOOKUP ---
        mcc = txn_payload.get("mcc")
        if mcc and mcc in self.mcc_map:
            print(f"MCC Match: {mcc} -> {self.mcc_map[mcc]}")
            result["category_name"] = self.mcc_map[mcc]
            result["confidence"] = 0.95
            result["source"] = "mcc"
            self._finalize(result, txn_payload)
            return result

        # --- Step 4: MERCHANT MEMORY ---
        merch_name = txn_payload.get("merchant_name") or txn_payload.get("beneficiary_name") or ""
        merch_key = self.normalize_text(merch_name).replace(" ", "")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT category_name, confidence FROM merchant_category_memory WHERE merchant_key = ?", (merch_key,))
        row = cursor.fetchone()
        
        if row:
            print(f"Merchant Match: {merch_key} -> {row[0]} ({row[1]})")
            result["category_name"] = row[0]
            result["confidence"] = row[1]
            result["source"] = "merchant_memory"
            
            # Update usage
            cursor.execute("UPDATE merchant_category_memory SET usage_count = usage_count + 1, last_seen = ? WHERE merchant_key = ?", 
                           (datetime.now().isoformat(), merch_key))
            self.conn.commit()
            
            self._finalize(result, txn_payload)
            return result

        # Capture embedding for learning loop
        current_embedding = None

        # --- Step 5: EMBEDDING MEMORY ---
        if OPENAI_AVAILABLE and clean_desc:
            current_embedding = self.get_embedding(clean_desc)
            if current_embedding:
                # Fetch all embeddings (In prod, use vector DB)
                cursor.execute("SELECT category_name, embedding FROM embedding_memory WHERE embedding IS NOT NULL")
                rows = cursor.fetchall()
                
                best_score = 0
                best_cat = None
                
                for r_cat, r_emb_json in rows:
                    if not r_emb_json: continue
                    r_emb = json.loads(r_emb_json)
                    score = self.cosine_similarity(current_embedding, r_emb)
                    if score > best_score:
                        best_score = score
                        best_cat = r_cat
                print(f"Best Embedding Match: {best_cat} ({best_score})")
                if best_score >= 0.7:
                    print(f"Embedding Match: {clean_desc} -> {best_cat} ({best_score})")
                    result["category_name"] = best_cat
                    result["confidence"] = round(best_score, 4)
                    result["source"] = "embedding_memory"
                    
                    self._finalize(result, txn_payload, current_embedding)
                    return result
        
        # --- Step 6: AI FALLBACK ---
        if OPENAI_AVAILABLE:
            try:
                print("Fallback to AI...")
                # ... (Prompt logic remains same) ...
                prompt = f"""
                Classify this transaction into exactly one of these categories: {', '.join(self.categories)}.
                Transaction: {clean_desc}, Amount: {amount}, Mode: {mode}, Beneficiary: {merch_name}.
                Return JSON only: {{"category_name": "...", "confidence": 0.XX}}
                """
                
                response = asyncio.run(client.get_response(system_prompt="You are a transaction classifier.", user_prompt=prompt, json_mode = True, model = LLM_DEPLOYMENT))
                
                ai_content = response.content
                ai_json = json.loads(ai_content)
                print(f"AI Response: {ai_json}")
                
                # Validation
                if ai_json["category_name"] in self.categories:
                    result["category_name"] = ai_json["category_name"]
                    result["confidence"] = ai_json.get("confidence", 0.80)
                    result["source"] = "ai"
                else:
                    # Fallback if hallucinated
                    result["category_name"] = "Transfers"
                    result["confidence"] = 0.5
                    result["source"] = "ai_fail_safe"

            except Exception as e:
                print(f"AI Error: {e}")
        
        # Default if everything fails
        if not result["category_name"]:
             result["category_name"] = "Transfers"
             result["confidence"] = 0.0
             result["source"] = "unknown"

        self._finalize(result, txn_payload, current_embedding)
        return result

    def _finalize(self, result, original_payload, embedding=None):
        """Step 7: Post-Processing & Persistence"""
        print(f"Final Decision: {result['category_name']} ({result['source']}, {result['confidence']})")
        
        cursor = self.conn.cursor()
        clean_desc = result["clean_description"]
        
        # 1. Insert into transactions table
        cursor.execute("""
            INSERT INTO transactions (
                transaction_id, account_id, account_name, transaction_date, amount, currency,
                transaction_type, beneficiary_name, remarks, merchant_name, mcc, mode,
                raw_description, clean_description, category_name, confidence, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result["transaction_id"],
            original_payload.get("account_id"),
            original_payload.get("account_name"),
            original_payload.get("transaction_date"),
            original_payload.get("amount"),
            original_payload.get("currency"),
            original_payload.get("transaction_type"),
            original_payload.get("beneficiary_name"),
            original_payload.get("remarks"),
            original_payload.get("merchant_name"),
            original_payload.get("mcc"),
            original_payload.get("mode"),
            original_payload.get("raw_description"),
            clean_desc,
            result["category_name"],
            result["confidence"],
            result["source"]
        ))
        
        # 2. Learning Loop
        if result["source"] == "ai" and result["confidence"] >= 0.85:
            print("  >> Learning from AI decision...")
            
            # A. Update Merchant Memory
            merch_name = original_payload.get("merchant_name") or original_payload.get("beneficiary_name")
            if merch_name:
                merch_key = self.normalize_text(merch_name).replace(" ", "")
                if merch_key and len(merch_key) > 2:
                    cursor.execute("SELECT merchant_key FROM merchant_category_memory WHERE merchant_key = ?", (merch_key,))
                    if not cursor.fetchone():
                        print(f"  >> Learning Merchant: {merch_name} -> {result['category_name']}")
                        cursor.execute("""
                            INSERT INTO merchant_category_memory 
                            (merchant_key, merchant_display_name, category_name, confidence, source, first_seen, last_seen, usage_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            merch_key, merch_name, result['category_name'], 0.90, 'ai_learned', 
                            datetime.now().isoformat(), datetime.now().isoformat(), 1
                        ))

            # B. Update Embedding Memory
            if embedding and clean_desc:
                # Check if similarity effectively exists (skip duplicates)
                # In a real vector DB we search near neighbors. Here we check exact pattern text for simplicity or minimal overlap
                cursor.execute("SELECT id FROM embedding_memory WHERE pattern_text = ?", (clean_desc,))
                if not cursor.fetchone():
                    print(f"  >> Learning Embedding Pattern: '{clean_desc}' -> {result['category_name']}")
                    emb_json = json.dumps(embedding)
                    cursor.execute("""
                        INSERT INTO embedding_memory 
                        (pattern_text, category_name, embedding, usage_count, first_seen, last_seen)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        clean_desc, result['category_name'], emb_json, 1, 
                        datetime.now().isoformat(), datetime.now().isoformat()
                    ))

        self.conn.commit()

    def close(self):
        self.conn.close()

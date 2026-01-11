
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
import uuid, os
from datetime import datetime
from src.processes.pipeline import TransactionPipeline

DB_FILE = os.path.join(os.getcwd(), "database", "transactions.db")

app = FastAPI(title="Transaction Categorization Engine API")

# Initialize Pipeline (Shared instance)
# In production, consider lifespan events for setup/teardown
pipeline = TransactionPipeline()

# --- Models ---

class TransactionInput(BaseModel):
    transaction_id: Optional[str] = None
    account_id: str
    account_name: str
    transaction_date: str
    amount: float
    currency: str
    transaction_type: str
    beneficiary_name: Optional[str] = None
    remarks: Optional[str] = None
    merchant_name: Optional[str] = None
    mcc: Optional[str] = None
    mode: str
    raw_description: Optional[str] = None

class CategorizationResult(BaseModel):
    transaction_id: str
    clean_description: str
    category_name: str
    confidence: float
    source: str
    # Enriched fields for UI
    amount: float
    currency: str
    transaction_type: str
    beneficiary_name: Optional[str]
    remarks: Optional[str]
    merchant_name: Optional[str]
    mcc: Optional[str]
    mode: str

class TransactionRecord(BaseModel):
    transaction_id: str
    transaction_date: str
    amount: float
    currency: str
    transaction_type: str
    beneficiary_name: Optional[str]
    remarks: Optional[str]
    merchant_name: Optional[str]
    mcc: Optional[str]
    mode: Optional[str]
    clean_description: Optional[str]
    raw_description: Optional[str]
    category_name: str
    confidence: float
    source: str

# --- Endpoints ---

@app.post("/categorize", response_model=CategorizationResult)
def categorize_transaction(txn: TransactionInput):
    """
    Real-time transaction categorization.
    """
    # 1. Prepare Payload
    payload = txn.model_dump()
    if not payload.get("transaction_id"):
        payload["transaction_id"] = f"txn_{uuid.uuid4()}"
    
    # 2. Run Pipeline
    try:
        result = pipeline.categorize(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return CategorizationResult(
        transaction_id=result["transaction_id"],
        clean_description=result["clean_description"],
        category_name=result["category_name"],
        confidence=result["confidence"],
        source=result["source"],
        # Input echo
        amount=txn.amount,
        currency=txn.currency,
        transaction_type=txn.transaction_type,
        beneficiary_name=txn.beneficiary_name,
        remarks=txn.remarks,
        merchant_name=txn.merchant_name,
        mcc=txn.mcc,
        mode=txn.mode
    )

@app.get("/transactions", response_model=List[TransactionRecord])
def get_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50
):
    """
    Fetch transaction history with filters.
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND transaction_date >= ?"
        params.append(start_date)
        
    if end_date:
        query += " AND transaction_date <= ?"
        params.append(end_date)
        
    if category:
        query += " AND category_name = ?"
        params.append(category)
        
    query += " ORDER BY transaction_date DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append(TransactionRecord(
            transaction_id=row["transaction_id"],
            transaction_date=row["transaction_date"],
            amount=row["amount"],
            currency=row["currency"],
            transaction_type=row["transaction_type"],
            beneficiary_name=row["beneficiary_name"],
            remarks=row["remarks"],
            merchant_name=row["merchant_name"],
            mcc=row["mcc"],
            mode=row["mode"],
            clean_description=row["clean_description"],
            raw_description=row["raw_description"],
            category_name=row["category_name"] or "Uncategorized",
            confidence=row["confidence"] or 0.0,
            source=row["source"] or "unknown"
        ))
        
    return results

@app.get("/categories")
def get_categories():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT category_name, description FROM categories")
    cats = [{"name": row[0], "description": row[1]} for row in cursor.fetchall()]
    conn.close()
    return cats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import psycopg2
import os
from datetime import datetime
from psycopg2.extras import RealDictCursor
import json
import fitz
import re
from datetime import datetime
from decimal import Decimal

def format_transactions_for_llm(transactions):
    clean_list = []

    for tx in transactions:
        clean_tx = {}
        for key, value in tx.items():
            if isinstance(value, datetime):
                clean_tx[key] = value.isoformat()
            elif isinstance(value, Decimal):
                clean_tx[key] = float(value)
            else:
                clean_tx[key] = value

        clean_list.append(clean_tx)

    return json.dumps(clean_list, indent=2)

def get_connection():
    return psycopg2.connect(os.getenv("NEON_DB_URL"))

def get_month_transactions():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    now = datetime.now()
    year = now.year
    month = now.month

    query = """
        SELECT *
        FROM transactions
        WHERE EXTRACT(YEAR FROM transaction_date) = %s
          AND EXTRACT(MONTH FROM transaction_date) = %s
        ORDER BY transaction_date DESC;
    """

    cursor.execute(query, (year, month))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


def decode_json(text):
    try:
        decoder = json.JSONDecoder()
        pos = 0
        while pos < len(text):
            try:
                obj, pos = decoder.raw_decode(text, pos)
                return obj
            except:
                pos += 1
    except:
        return None



def extract_text_from_pdf(file_bytes):
    pdf = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text()
    return text


def extract_salary(text):
    match = re.search(r"Rs\.?\s?([\d,]+\.\d{2})", text)
    if match:
        num = match.group(1).replace(",", "")
        return int(float(num))
    
    candidates = re.findall(r"[\d,]+\.\d{2}", text)
    if candidates:
        values = [float(x.replace(",", "")) for x in candidates]
        return int(max(values))

    return None

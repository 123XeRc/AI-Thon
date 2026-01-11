from dotenv import load_dotenv
from src.utils_helpers import *
from src.adapters.azure_openai import async_openai_client
from src.prompts import *
load_dotenv()
CATEGORIES = [
    "Food & Dining",
    "Groceries",
    "Travel & Transport",
    "Utilities",
    "Shopping",
    "Health & Wellness",
    "Entertainment",
    "Transfers",
    "Investment",
    "Education",
    "Pets",
    "Home Services",
    "Charity",
    "Insurance",
    "Taxes",
    "Office & Business",
    "Gifts & Donations",
    "Kids",
    "Personal Care"
]


async def process_budget_analysis(payslip_file):
        pdf_bytes = await payslip_file.read()
        pdf_text = extract_text_from_pdf(pdf_bytes)

        income = extract_salary(pdf_text)
        if income is None:
            income=80000
        
        budget = await generate_budget_from_income(income)

        transactions_list = get_month_transactions()
        limited_tx_list = transactions_list[:10]
        transaction = format_transactions_for_llm(limited_tx_list)

        analysis = await analyze_budget(transaction, budget)

        print(analysis)
        return {
            "extracted_income": income,
            "generated_budget": budget,
            "analysis": analysis
        }

async def generate_budget_from_income(income):

    prompt = USER_BUDGET_TEMPLATE.format(
        income=income,
        categories=json.dumps(CATEGORIES, indent=2)
    )
    raw_response = await async_openai_client.get_response(
        system_prompt=SYSTEM_BUDGET_PROMPT,
        user_prompt=prompt,
        json_mode=False
    )
    response=decode_json(raw_response['content'])
    
    return response


async def analyze_budget(transactions, budget):

    prompt = USER_ANALYSIS_TEMPLATE.format(
        budget=budget,
        transactions=transactions
    )
    
    raw_response = await async_openai_client.get_response(
        system_prompt=SYSTEM_ANALYSIS_PROMPT,
        user_prompt=prompt,
        json_mode=True
    )
    response=decode_json(raw_response['content'])
    return response
## Generate FastAPI Server + Endpoint

Create a FastAPI backend with CORS enabled and a single POST endpoint /budget_analyse.

The endpoint should accept a file upload (PDF payslip), pass that file into a function named process_budget_analysis, await the result, and return the JSON response.

Structure the code cleanly and allow modular integration

## Generate Azure OpenAI Async Adapter
Generate a Python class named AsyncAzureOpenAIHelper that wraps Azure OpenAI Chat Completions API.

Requirements:
- async API calls using AsyncAzureOpenAI
- retries with exponential backoff
- logs attempts, errors, token usage, and latency
- method get_response(system_prompt, user_prompt, json_mode=True|False)
- supports Azure response_format={"type":"json"}
- returns dict: {content, input_tokens, output_tokens, latency_seconds}
- loads credentials from environment variables
- globally expose async_openai_client = AsyncAzureOpenAIHelper()


## Generate a complete folder structure:

src/
    adapters/
        azure_openai.py
        loggers.py
    prompts/
        prompts.py
    utils.py
    utils_helpers.py
main.py

Each file should contain the correct imports and code references.

## Generate Budget Processing Workflow

Generate a function process_budget_analysis(payslip_file) that:

1. Reads PDF bytes
2. Extracts text with extract_text_from_pdf
3. Extracts salary with extract_salary
4. Falls back to default income if extraction fails
5. Calls generate_budget_from_income(income)
6. Fetches monthly transactions with get_month_transactions()
7. Limits to top 10 transactions
8. Formats transactions with format_transactions_for_llm()
9. Calls analyze_budget(transaction_json, budget_json)
10. Returns structured JSON:
    {
      "extracted_income": income,
      "generated_budget": [...],
      "analysis": {...}
    }


## Generate Prompt Templates Module

Generate prompts.py containing ONLY string templates — no functions.

Include:
- SYSTEM_BUDGET_PROMPT
- USER_BUDGET_TEMPLATE
- SYSTEM_ANALYSIS_PROMPT
- USER_ANALYSIS_TEMPLATE
- CATEGORIES list

Ensure budget prompt:
- Requires output in JSON array
- Requires all categories to appear exactly once
- Total sum must equal income
- No extra text

Ensure analysis prompt:
- Returns concise JSON with overspending_categories and recommendations


## Generate Budget Creation Function
Create async function generate_budget_from_income(income).

It should:
- build user prompt using USER_BUDGET_TEMPLATE
- include categories via json.dumps()
- call async_openai_client.get_response(json_mode=True)
- decode JSON response with decode_json
- return parsed JSON list

## Generate Budget Analysis Function

Generate async function analyze_budget(transactions, budget).

It must:
- format user prompt from USER_ANALYSIS_TEMPLATE
- call async_openai_client.get_response(json_mode=True)
- parse JSON result with decode_json
- return overspending categories + recommendations


## Generate a full production-ready financial analysis backend with the following components:

1. FastAPI server with /budget_analyse endpoint
2. Async Azure OpenAI adapter with retry logic
3. Budget generation using LLM with strict JSON output
4. Financial analysis comparing budget vs transactions
5. PostgreSQL integration to fetch monthly transactions
6. PDF salary extraction
7. Prompt templates in a separate module
8. Utility functions to format and sanitize data
9. Full folder structure
10. All code in separate files with correct imports

Ensure:
- JSON-only LLM output
- No hallucinations
- Robust error handling
- All code is ready to run

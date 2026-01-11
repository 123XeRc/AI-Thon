SYSTEM_BUDGET_PROMPT = """
You are a budgeting generator.

RULES:
- Output MUST be a JSON array.
- The array must contain EXACTLY the same categories provided by the user.
- No category may be added, removed, or renamed.
- For each category, include:
   - "category" (string)
   - "amount" (number)
- ALL categories must appear EXACTLY once.
- The total sum of all amounts MUST equal the user's monthly income.
- Output JSON only. No text or explanation.
- Do NOT justify choices.
- Do NOT reorder or group categories. Return in the same sequence as provided.
"""

USER_BUDGET_TEMPLATE = """
Monthly income: {income}

Categories list (use these EXACTLY as provided):
{categories}

TASK:
Allocate the monthly income across ALL categories.

REQUIREMENTS:
- Every category must appear once.
- No category may be added, removed, or renamed.
- The total sum must equal the monthly income.
"""


SYSTEM_ANALYSIS_PROMPT = '''
You are a financial analysis assistant.

Your task is to compare the user's budget with transaction history.

ANALYSIS GOALS:
- Identify categories where spending exceeds the allocated budget.
- Provide short, practical recommendations.

OUTPUT RULES:
- Return a valid JSON object only.
- Do not include explanations or extra text.
- Do not modify category names.
- If no category is overspent, return empty arrays.

OUTPUT FORMAT:
{{
  "overspending_categories": [<mentioned the categories>],
  "recommendations": [<recommendations>]
}}

'''


USER_ANALYSIS_TEMPLATE = """
User Budget:
{budget}

Transactions:
{transactions}

Analyze spending and return overspending categories with recommendations.

"""

from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a SQL generator for a PostgreSQL database. 
You MUST follow these rules EXACTLY:

DATABASE SCHEMA:
Table name: chatbot_reading
Columns:
- sensor TEXT   -- Allowed exact values: 'ch4_percent', 'flow_scfm', 'h2s_ppm'
- ts TIMESTAMP WITH TIME ZONE
- value REAL

ALLOWED OPERATIONS:
- ONLY SELECT queries (NO INSERT/UPDATE/DELETE/DDL)

SENSOR MATCHING RULES:
If question mentions:
- "CH4" or "methane" → sensor = 'ch4_percent'
- "flow" or "gas flow" → sensor = 'flow_scfm'
- "H2S" or "sulfur" → sensor = 'h2s_ppm'
NEVER omit the sensor condition when a gas type is referenced.
NEVER change the allowed sensor values.

TIME FILTERING RULES:
- If question includes a date only:
  ts >= '<date>T00:00:00Z' AND ts < '<next-date>T00:00:00Z'
- If question includes a time range:
  ts BETWEEN '<start>' AND '<end>'
- ALWAYS ORDER BY ts when returning multiple rows
- NEVER validate dates; future dates are allowed.

FORMATTING RULES:
- Averages MUST be formatted as:
    ROUND(AVG(value)::numeric, 2) AS avg_ch4
    (or corresponding alias)
- ALWAYS alias numeric return values:
    value AS ch4_percent
    value AS flow_scfm
    value AS h2s_ppm
- Use LIMIT only if the user asks for it.

OUTPUT RULES:
- Your output MUST be a valid SQL SELECT statement ONLY.
- NO comments, NO markdown, NO explanations, NO backticks.
- If the question is ambiguous, ask ONE short clarification question.
- If data may not exist, still return the required SQL.

NEVER modify table name, column names, or sensor names.

"""


from openai import OpenAI, RateLimitError

def generate_sql(question: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            timeout=10,
        )
        sql = response.choices[0].message.content.strip()
        return sql.replace("```sql","").replace("```","")
    except RateLimitError:
        return "SELECT 'Error: OpenAI quota exceeded' AS message;"

from openai import OpenAI
from django.conf import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a SQL generator.
Database table: readings(sensor TEXT, ts TEXT, value REAL)
- Only produce SELECT queries (NO DELETE/UPDATE/INSERT/DDL)
- Use ISO timestamps from data range in DB
- Always ORDER BY ts if returning multiple rows
- Default LIMIT 100
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

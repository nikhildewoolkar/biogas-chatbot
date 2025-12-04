# chatbot/views_api.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from .models import Reading
from django.conf import settings
from openai import OpenAI, RateLimitError

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

def allow_select_only(sql):
    return sql.lower().strip().startswith("select")

def execute_sql(sql):
    if not allow_select_only(sql):
        return JsonResponse({"error": "Only SELECT allowed"}, status=400)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [c[0] for c in cursor.description]

    return JsonResponse({"rows": [dict(zip(cols, r)) for r in rows]}, status=200)


@csrf_exempt
def chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    data = json.loads(request.body)
    question = data.get("question", "")
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
        )
        sql = response.choices[0].message.content.strip()
        sql = sql.replace("```sql", "").replace("```", "")
    except RateLimitError:
        sql = "SELECT 'Error: OpenAI quota exceeded' AS message"

    # Execute SQL
    result = execute_sql(sql)
    result_json = json.loads(result.content)

    return JsonResponse({
        "question": question,
        "sql": sql,
        "rows": result_json.get("rows", []),
        "clarificationAsked": False
    })


def query(request):
    sql = request.GET.get("sql", "")
    return execute_sql(sql)


def schema(request):
    return JsonResponse({
        "columns": ["sensor", "ts", "value"]
    })


def health(request):
    return JsonResponse({"status": "ok"})

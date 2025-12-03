# chatbot/views_api.py

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from .models import Readings
from django.conf import settings
from openai import OpenAI, RateLimitError

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """
You are a SQL generator for a database table:
readings(sensor TEXT, ts TEXT, value REAL)

Rules:
- Only generate SELECT queries (NO insert/update/delete/drop)
- Use ISO UTC timestamps
- Default LIMIT 100 if user doesn’t specify
- ORDER BY ts when returning multiple rows
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

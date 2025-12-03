from django.db import connection

def execute_sql(sql):
    if not sql.lower().strip().startswith("select"):
        return {"error": "Only SELECT allowed"}

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

    return {"rows": [dict(zip(columns, row)) for row in rows]}

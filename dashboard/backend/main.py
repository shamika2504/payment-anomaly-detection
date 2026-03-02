import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    database_url = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL found: {database_url is not None}")
    if database_url:
        return psycopg2.connect(database_url, sslmode='require')
    return psycopg2.connect(
        host="localhost",
        port=5433,
        database="payments",
        user="admin",
        password="admin123"
    )

@app.get("/stats")
def get_stats():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            COUNT(*) as total_transactions,
            SUM(is_fraud_predicted) as total_fraud,
            ROUND(AVG(amount)::numeric, 2) as avg_amount,
            ROUND((SUM(is_fraud_predicted) * 100.0 / COUNT(*))::numeric, 2) as fraud_rate
        FROM transactions
    """)
    stats = cur.fetchone()
    conn.close()
    return stats

@app.get("/fraud-by-hour")
def fraud_by_hour():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT hour_of_day, COUNT(*) as total,
               SUM(is_fraud_predicted) as fraud_count
        FROM transactions
        GROUP BY hour_of_day
        ORDER BY hour_of_day
    """)
    rows = cur.fetchall()
    conn.close()

    # Fill in missing hours with zeros
    data = {r["hour_of_day"]: r for r in rows}
    result = []
    for hour in range(24):
        if hour in data:
            result.append(data[hour])
        else:
            result.append({"hour_of_day": hour, "total": 0, "fraud_count": 0})
    return result

@app.get("/recent-fraud")
def recent_fraud():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT transaction_id, amount, merchant, currency,
               hour_of_day, is_international, fraud_score
        FROM transactions
        WHERE is_fraud_predicted = 1
        ORDER BY processed_at DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/amount-distribution")
def amount_distribution():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            CASE
                WHEN amount < 100 THEN '0-100'
                WHEN amount < 300 THEN '100-300'
                WHEN amount < 600 THEN '300-600'
                WHEN amount < 1000 THEN '600-1000'
                ELSE '1000+'
            END as range,
            COUNT(*) as count
        FROM transactions
        GROUP BY range
        ORDER BY range
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
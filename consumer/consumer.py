import json
import pickle
import time
import pandas as pd
import numpy as np
import psycopg2
from kafka import KafkaConsumer
from datetime import datetime

# Load trained model
with open("model/fraud_model.pkl", "rb") as f:
    model = pickle.load(f)

print("Model loaded successfully.")

# Connect to PostgreSQL (port 5433 since we remapped)
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="payments",
    user="admin",
    password="admin123"
)
cursor = conn.cursor()
print("Connected to PostgreSQL.")

# Connect to Kafka
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='fraud-detector'
)
print("Connected to Kafka. Listening for transactions...")

FEATURES = ["amount", "hour_of_day", "day_of_week", "is_international", "previous_txn_amount"]

count = 0
fraud_count = 0
batch = []
BATCH_SIZE = 100

for message in consumer:
    txn = message.value

    # Feature extraction
    features = pd.DataFrame([{
        "amount": txn["amount"],
        "hour_of_day": txn["hour_of_day"],
        "day_of_week": txn["day_of_week"],
        "is_international": txn["is_international"],
        "previous_txn_amount": txn["previous_txn_amount"],
    }])

    fraud_score = model.predict_proba(features)[0][1]
    # Adaptive threshold — flag if score > 0.5
    is_fraud_predicted = int(fraud_score > 0.5)

    batch.append((
        txn["transaction_id"],
        txn["user_id"],
        txn["amount"],
        txn["merchant"],
        txn["currency"],
        txn["hour_of_day"],
        txn["day_of_week"],
        txn["is_international"],
        txn["previous_txn_amount"],
        float(fraud_score),
        is_fraud_predicted,
        txn["timestamp"]
    ))

    count += 1
    if is_fraud_predicted:
        fraud_count += 1

    # Write in batches of 100 for performance
    if len(batch) >= BATCH_SIZE:
        cursor.executemany("""
            INSERT INTO transactions (
                transaction_id, user_id, amount, merchant, currency,
                hour_of_day, day_of_week, is_international, previous_txn_amount,
                fraud_score, is_fraud_predicted, timestamp
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, batch)
        conn.commit()
        batch = []
        print(f"[{datetime.utcnow().isoformat()}] Processed: {count} txns | Fraud flagged: {fraud_count} ({fraud_count/count*100:.1f}%)")
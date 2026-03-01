import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

fake = Faker()
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

MERCHANTS = ['Amazon', 'Walmart', 'Target', 'Uber', 'Netflix', 'Shell', 'McDonald\'s', 'Apple']
CURRENCIES = ['USD', 'EUR', 'GBP', 'INR']

def generate_transaction():
    is_fraud = random.random() < 0.02  # 2% fraud rate

    if is_fraud:
        amount = round(random.uniform(800, 5000), 2)   # unusually high
        hour = random.randint(0, 4)                     # odd hours
    else:
        amount = round(random.uniform(1, 400), 2)
        hour = random.randint(8, 22)

    return {
        "transaction_id": fake.uuid4(),
        "user_id": fake.uuid4(),
        "amount": amount,
        "merchant": random.choice(MERCHANTS),
        "currency": random.choice(CURRENCIES),
        "hour_of_day": hour,
        "day_of_week": random.randint(0, 6),
        "is_international": random.choice([0, 1]),
        "previous_txn_amount": round(random.uniform(1, 500), 2),
        "is_fraud": int(is_fraud),
        "timestamp": datetime.utcnow().isoformat()
    }

count = 0
print("Starting transaction producer... Press Ctrl+C to stop.")

while True:
    txn = generate_transaction()
    producer.send('transactions', value=txn)
    count += 1
    if count % 1000 == 0:
        print(f"[{datetime.utcnow().isoformat()}] Sent {count} transactions")
    time.sleep(0.00002)  # ~50K transactions/sec
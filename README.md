# Real-Time Payment Fraud Detection Pipeline

A production-grade streaming data pipeline that detects fraudulent payment transactions in real time using Kafka, XGBoost, PostgreSQL, and a live React dashboard.

## Architecture
```
Transaction Producer → Apache Kafka → Fraud Detection Consumer → PostgreSQL → FastAPI → React Dashboard
```

## Tech Stack

- **Streaming**: Apache Kafka + Zookeeper
- **ML Model**: XGBoost with MLflow experiment tracking
- **Backend API**: FastAPI (Python)
- **Frontend**: React + Recharts
- **Database**: PostgreSQL
- **Infrastructure**: Docker + Docker Compose

## Features

- Simulates 50,000+ transactions/second through Kafka
- Real-time ML inference with sub-100ms latency
- Adaptive fraud scoring threshold (0.5) to minimize false positives
- Live dashboard auto-refreshing every 5 seconds
- Batch writes to PostgreSQL (100 transactions/batch) for performance
- MLflow experiment tracking for model versioning

## Results

- **Precision**: 0.70 — 70% of flagged transactions are genuine fraud
- **Recall**: 0.94 — catches 94% of all fraudulent transactions  
- **F1 Score**: 0.80
- Prioritized high recall since missing fraud is more costly than false positives

## Project Structure
```
payment-anomaly-detection/
├── producer/         # Kafka transaction producer
├── consumer/         # Fraud detection consumer + PostgreSQL writer
├── model/            # XGBoost training + MLflow tracking
├── dashboard/
│   ├── backend/      # FastAPI REST API
│   └── frontend/     # React dashboard
└── docker-compose.yml
```

## Running Locally

**Prerequisites**: Docker Desktop, Python 3.12+, Node.js
```bash
# Start infrastructure
docker compose up -d

# Install dependencies and train model
pip install -r model/requirements.txt
python model/train_model.py

# Start producer (Terminal 1)
pip install -r producer/requirements.txt
python producer/producer.py

# Start consumer (Terminal 2)
pip install -r consumer/requirements.txt
python consumer/consumer.py

# Start API (Terminal 3)
cd dashboard/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Start dashboard (Terminal 4)
cd dashboard/frontend
npm install
npm start
```

Open https://payment-anomaly-detection.vercel.app to view the dashboard.
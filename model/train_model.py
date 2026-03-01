import pandas as pd
import numpy as np
import xgboost as xgb
import mlflow
import mlflow.xgboost
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder

# Generate synthetic training data
np.random.seed(42)
n = 100000
legit_n = int(n * 0.98)
fraud_n = int(n * 0.02)

legit = pd.DataFrame({
    "amount": np.clip(np.random.exponential(scale=80, size=legit_n), 1, 1000),
    "hour_of_day": np.random.randint(6, 23, legit_n),      # daytime heavy
    "day_of_week": np.random.randint(0, 7, legit_n),
    "is_international": np.random.choice([0, 1], legit_n, p=[0.85, 0.15]),
    "previous_txn_amount": np.clip(np.random.exponential(scale=80, size=legit_n), 1, 1000),
    "is_fraud": 0
})

fraud = pd.DataFrame({
    "amount": np.where(
        np.random.rand(fraud_n) < 0.75,
        np.random.uniform(500, 5000, fraud_n),   # 75% high value
        np.random.uniform(10, 400, fraud_n)       # 25% blend in
    ),
    "hour_of_day": np.where(
        np.random.rand(fraud_n) < 0.70,
        np.random.randint(0, 5, fraud_n),         # 70% late night
        np.random.randint(6, 23, fraud_n)         # 30% blend in
    ),
    "day_of_week": np.random.randint(0, 7, fraud_n),
    "is_international": np.random.choice([0, 1], fraud_n, p=[0.4, 0.6]),
    "previous_txn_amount": np.clip(np.random.exponential(scale=40, size=fraud_n), 1, 500),
    "is_fraud": 1
})

df = pd.concat([legit, fraud]).sample(frac=1).reset_index(drop=True)

# Cap amounts to realistic range
df["amount"] = df["amount"].clip(1, 5000)
df["previous_txn_amount"] = df["previous_txn_amount"].clip(1, 5000)

X = df.drop("is_fraud", axis=1)
y = df["is_fraud"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train with MLflow tracking
mlflow.set_experiment("fraud-detection")

with mlflow.start_run():
    params = {
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1,
        "scale_pos_weight": 49,  # handles class imbalance (98:2 ratio)
        "use_label_encoder": False,
        "eval_metric": "logloss"
    }

    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)

    # Log to MLflow
    mlflow.log_params(params)
    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)
    mlflow.xgboost.log_model(model, "model")

    print(f"Precision: {precision:.2f}")
    print(f"Recall:    {recall:.2f}")
    print(f"F1 Score:  {f1:.2f}")

    # Save model locally for the consumer
    with open("model/fraud_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("Model saved to model/fraud_model.pkl")
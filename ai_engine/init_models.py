import os
import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
from statsmodels.tsa.statespace.sarimax import SARIMAX

# 1. ProjectCostPredictor (XGBoost)
def train_cost_predictor():
    print("Training ProjectCostPredictor (XGBoost)...")
    X = np.random.rand(100, 5) # budget, team_size, complexity, duration, historical_avg
    y = X[:, 0] * 1.2 + X[:, 1] * 5000 + np.random.normal(0, 1000, 100)
    model = XGBRegressor(n_estimators=100, learning_rate=0.05)
    model.fit(X, y)
    joblib.dump(model, "ai_engine/models/cost_predictor.joblib")
    print("Saved to ai_engine/models/cost_predictor.joblib")

# 2. RevenueForecaster (LightGBM)
def train_revenue_forecaster():
    print("Training RevenueForecaster (LightGBM)...")
    X = np.random.rand(100, 5)
    y = X[:, 0] * 2.0 + np.random.normal(0, 500, 100)
    model = LGBMRegressor(n_estimators=100, learning_rate=0.05, verbosity=-1)
    model.fit(X, y)
    joblib.dump(model, "ai_engine/models/revenue_forecaster.joblib")
    print("Saved to ai_engine/models/revenue_forecaster.joblib")

# 3. RiskClassifier (Random Forest)
def train_risk_classifier():
    print("Training RiskClassifier (Random Forest)...")
    X = np.random.rand(100, 5)
    y = (X[:, 2] > 0.7).astype(int) # High complexity -> High risk
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X, y)
    joblib.dump(model, "ai_engine/models/risk_classifier.joblib")
    print("Saved to ai_engine/models/risk_classifier.joblib")

# 3.5 EmployeeClassifier (Random Forest)
def train_employee_classifier():
    print("Training EmployeeClassifier (Random Forest)...")
    X = np.random.rand(100, 4) # tasks_completed, average_time, complexity, work_logs_count
    y = (X[:, 0] < 0.3).astype(int) # Low tasks -> Low performance
    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)
    joblib.dump(model, "ai_engine/models/employee_classifier.joblib")
    print("Saved to ai_engine/models/employee_classifier.joblib")

# 4. AnomalyDetector (Isolation Forest)
def train_anomaly_detector():
    print("Training AnomalyDetector (Isolation Forest)...")
    X = np.random.normal(5000, 1000, (200, 1)) # Normal expenses
    # Add anomalies
    X = np.vstack([X, [[25000], [30000], [50000]]])
    model = IsolationForest(contamination=0.05)
    model.fit(X)
    joblib.dump(model, "ai_engine/models/anomaly_detector.joblib")
    print("Saved to ai_engine/models/anomaly_detector.joblib")

# 5. Burn-Rate Autoencoder (PyTorch)
class Autoencoder(nn.Module):
    def __init__(self):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 2))
        self.decoder = nn.Sequential(nn.Linear(2, 5), nn.ReLU(), nn.Linear(5, 10))
    def forward(self, x):
        return self.decoder(self.encoder(x))

def save_autoencoder():
    print("Saving Burn-Rate Autoencoder (PyTorch)...")
    model = Autoencoder()
    torch.save(model.state_dict(), "ai_engine/models/burn_rate_autoencoder.pth")
    print("Saved to ai_engine/models/burn_rate_autoencoder.pth")

# 6. Cash Flow LSTM Shell
class CashFlowLSTM(nn.Module):
    def __init__(self):
        super(CashFlowLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=32, num_layers=2, bidirectional=True, batch_first=True)
        self.fc = nn.Linear(64, 1)
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

def save_lstm():
    print("Saving CashFlow LSTM (PyTorch)...")
    model = CashFlowLSTM()
    torch.save(model.state_dict(), "ai_engine/models/cashflow_lstm.pth")
    print("Saved to ai_engine/models/cashflow_lstm.pth")

if __name__ == "__main__":
    os.makedirs("ai_engine/models", exist_ok=True)
    train_cost_predictor()
    train_revenue_forecaster()
    train_risk_classifier()
    train_employee_classifier()
    train_anomaly_detector()
    save_autoencoder()
    save_lstm()
    print("\n✅ All P0 ML Models Initialized and Saved.")

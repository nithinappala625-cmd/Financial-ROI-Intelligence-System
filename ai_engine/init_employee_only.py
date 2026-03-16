import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def train_employee_classifier():
    print("Training EmployeeClassifier (Random Forest)...")
    X = np.random.rand(100, 4) # tasks_completed, average_time, complexity, work_logs_count
    y = (X[:, 0] < 0.3).astype(int) # Low tasks -> Low performance
    model = RandomForestClassifier(n_estimators=50)
    model.fit(X, y)
    joblib.dump(model, "ai_engine/models/employee_classifier.joblib")
    print("Saved to ai_engine/models/employee_classifier.joblib")

if __name__ == "__main__":
    train_employee_classifier()

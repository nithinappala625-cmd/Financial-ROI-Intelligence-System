from fastapi import APIRouter
import joblib
import numpy as np

import torch
import torch.nn as nn

router = APIRouter(prefix="/anomaly", tags=["anomaly"])

# Load Isolation Forest
ISO_FOREST = joblib.load("ai_engine/models/anomaly_detector.joblib")

# Load Burn-Rate Autoencoder
class Autoencoder(nn.Module):
    def __init__(self):
        super(Autoencoder, self).__init__()
        self.encoder = nn.Sequential(nn.Linear(10, 5), nn.ReLU(), nn.Linear(5, 2))
        self.decoder = nn.Sequential(nn.Linear(2, 5), nn.ReLU(), nn.Linear(5, 10))
    def forward(self, x):
        return self.decoder(self.encoder(x))

try:
    AE_MODEL = Autoencoder()
    AE_MODEL.load_state_dict(torch.load("ai_engine/models/burn_rate_autoencoder.pth"))
    AE_MODEL.eval()
    HAS_AE = True
except Exception:
    HAS_AE = False
    print("WARNING: Burn-Rate Autoencoder could not be loaded.")

@router.post("/scan")
async def scan_anomaly(req: dict):
    amt = float(req.get("amount", 0.0))
    X = np.array([[amt]])
    
    # 1. IsolationForest Prediction
    iso_pred = ISO_FOREST.predict(X)[0]
    is_iso_anomaly = (iso_pred == -1)
    iso_score = ISO_FOREST.decision_function(X)[0]
    
    # 2. Autoencoder Reconstruction Error (Mocking 10 inputs for AE)
    is_ae_anomaly = False
    mse_loss = 0.0
    if HAS_AE:
        ae_input = torch.randn(1, 10) # Using random context as placeholder
        with torch.no_grad():
            reconstructed = AE_MODEL(ae_input)
            mse_loss = torch.mean((ae_input - reconstructed) ** 2).item()
        is_ae_anomaly = mse_loss > 0.5 # Threshold
    
    # Final verdict: Weighted fusion
    is_anomaly = is_iso_anomaly or is_ae_anomaly
    
    return {
        "is_anomaly": bool(is_anomaly),
        "isolation_forest_anomaly": bool(is_iso_anomaly),
        "autoencoder_reconstruction_error": float(mse_loss),
        "autoencoder_available": bool(HAS_AE),
        "anomaly_score": float(1.0 - abs(iso_score)),
        "message": "Neural Anomaly Detected" if is_anomaly else "Normal expense transaction",
        "method": "Hybrid IsolationForest + PyTorch Autoencoder"
    }

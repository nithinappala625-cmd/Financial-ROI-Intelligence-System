"""
F018: CashFlowLSTM training — Bidirectional LSTM for 90-day forecasting.
2-layer 128 units; 24-month rolling window; MAPE < 15% month 1.
"""

import os
import json
import logging
import datetime
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")


class CashFlowLSTM(nn.Module):
    """Bidirectional LSTM for multi-horizon cash flow forecasting."""

    def __init__(self, input_size=3, hidden_size=128, num_layers=2, output_size=3, dropout=0.2):
        super(CashFlowLSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            bidirectional=True,
            batch_first=True,
            dropout=dropout,
        )
        self.attention = nn.Linear(hidden_size * 2, 1)
        self.fc1 = nn.Linear(hidden_size * 2, 64)
        self.fc2 = nn.Linear(64, output_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)  # (batch, seq, hidden*2)

        # Attention mechanism
        attn_weights = torch.softmax(self.attention(lstm_out), dim=1)
        context = torch.sum(attn_weights * lstm_out, dim=1)

        out = self.dropout(self.relu(self.fc1(context)))
        out = self.fc2(out)
        return out


def generate_synthetic_cashflow_data(n_months: int = 120, window_size: int = 24):
    """Generate synthetic monthly cash flow data with seasonality."""
    np.random.seed(42)

    t = np.arange(n_months)

    # Revenue with trend + seasonality
    revenue = 50000 + 500 * t + 10000 * np.sin(2 * np.pi * t / 12) + np.random.normal(0, 3000, n_months)
    # Expenses with trend
    expenses = 40000 + 300 * t + 5000 * np.sin(2 * np.pi * t / 12 + 1) + np.random.normal(0, 2000, n_months)
    # Net cash flow
    net_cf = revenue - expenses

    data = np.column_stack([revenue, expenses, net_cf])

    X_windows = []
    y_targets = []

    for i in range(window_size, len(data) - 3):
        X_windows.append(data[i - window_size:i])
        y_targets.append(data[i:i + 3, :].mean(axis=0))  # avg of next 3 months

    X = np.array(X_windows, dtype=np.float32)
    y = np.array(y_targets, dtype=np.float32)

    # Normalize
    X_mean, X_std = X.reshape(-1, 3).mean(axis=0), X.reshape(-1, 3).std(axis=0)
    X = (X - X_mean) / (X_std + 1e-8)
    y = (y - X_mean) / (X_std + 1e-8)

    return X, y, X_mean, X_std


def train_cashflow_lstm(
    epochs: int = 100,
    batch_size: int = 16,
    learning_rate: float = 0.001,
    hidden_size: int = 128,
) -> dict:
    """Train the CashFlowLSTM model."""
    logger.info("Training CashFlowLSTM (Bidirectional 2-layer)...")

    X, y, X_mean, X_std = generate_synthetic_cashflow_data()

    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    train_dataset = TensorDataset(
        torch.FloatTensor(X_train), torch.FloatTensor(y_train)
    )
    test_dataset = TensorDataset(
        torch.FloatTensor(X_test), torch.FloatTensor(y_test)
    )
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    model = CashFlowLSTM(input_size=3, hidden_size=hidden_size, output_size=3)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)

    best_val_loss = float("inf")
    train_losses = []
    val_losses = []

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            output = model(X_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            epoch_loss += loss.item()

        avg_train_loss = epoch_loss / len(train_loader)
        train_losses.append(avg_train_loss)

        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for X_batch, y_batch in test_loader:
                output = model(X_batch)
                val_loss += criterion(output, y_batch).item()
        avg_val_loss = val_loss / len(test_loader)
        val_losses.append(avg_val_loss)

        scheduler.step(avg_val_loss)

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), os.path.join(MODEL_DIR, "cashflow_lstm.pth"))

        if (epoch + 1) % 20 == 0:
            logger.info(f"Epoch {epoch+1}/{epochs} — Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}")

    # Compute MAPE on denormalized test predictions
    model.eval()
    all_preds = []
    all_targets = []
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            preds = model(X_batch)
            all_preds.append(preds.numpy())
            all_targets.append(y_batch.numpy())

    all_preds = np.vstack(all_preds)
    all_targets = np.vstack(all_targets)

    # Denormalize
    pred_denorm = all_preds * (X_std + 1e-8) + X_mean
    target_denorm = all_targets * (X_std + 1e-8) + X_mean

    mask = target_denorm != 0
    mape = np.mean(np.abs((target_denorm[mask] - pred_denorm[mask]) / target_denorm[mask])) * 100

    # Save normalization params alongside model
    norm_params = {"mean": X_mean.tolist(), "std": X_std.tolist()}
    with open(os.path.join(MODEL_DIR, "cashflow_lstm_norm.json"), "w") as f:
        json.dump(norm_params, f)

    metrics = {
        "best_val_loss": round(float(best_val_loss), 6),
        "final_train_loss": round(float(train_losses[-1]), 6),
        "mape_pct": round(float(mape), 2),
        "epochs_trained": epochs,
        "hidden_size": hidden_size,
        "architecture": "BiLSTM-Attention 2x128",
        "trained_at": str(datetime.datetime.now()),
    }

    logger.info(f"CashFlow LSTM trained — Val Loss={best_val_loss:.6f}, MAPE={mape:.2f}%")

    if mape > 15.0:
        logger.warning(f"MAPE {mape:.2f}% exceeds target 15%!")

    return metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    metrics = train_cashflow_lstm(epochs=50)
    print(f"\nTraining complete: {json.dumps(metrics, indent=2)}")

from app.repositories.base_repo import BaseRepo
from app.models.ai_prediction import AIPrediction


class AIPredictionRepo(BaseRepo[AIPrediction]):
    """AI Prediction record implementation instances."""

    def __init__(self):
        super().__init__(AIPrediction)


ai_prediction_repo = AIPredictionRepo()

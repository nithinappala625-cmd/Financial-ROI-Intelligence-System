from app.repositories.base_repo import BaseRepo
from app.models.alert import Alert


class AlertRepo(BaseRepo[Alert]):
    """System functional alert objects operations."""

    def __init__(self):
        super().__init__(Alert)


alert_repo = AlertRepo()

from app.repositories.base_repo import BaseRepo
from app.models.work_log import WorkLog


class WorkLogRepo(BaseRepo[WorkLog]):
    """Work log basic implementation instance."""

    def __init__(self):
        super().__init__(WorkLog)


work_log_repo = WorkLogRepo()

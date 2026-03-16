from app.repositories.base_repo import BaseRepo
from app.models.project import Project


class ProjectRepo(BaseRepo[Project]):
    """Project repository for basic project records implementation CRUD."""

    def __init__(self):
        super().__init__(Project)


project_repo = ProjectRepo()

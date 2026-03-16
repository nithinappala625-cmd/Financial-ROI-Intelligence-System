from app.repositories.base_repo import BaseRepo
from app.models.project_assignment import ProjectAssignment


class ProjectAssignmentRepo(BaseRepo[ProjectAssignment]):
    """Employee project assignments repository wrapper."""

    def __init__(self):
        super().__init__(ProjectAssignment)


project_assignment_repo = ProjectAssignmentRepo()

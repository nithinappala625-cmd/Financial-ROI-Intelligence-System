from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProjectAssignmentBase(BaseModel):
    project_id: int
    employee_id: int
    role_in_project: Optional[str] = None
    is_active: bool = True


class ProjectAssignmentCreate(ProjectAssignmentBase):
    pass


class ProjectAssignmentUpdate(BaseModel):
    role_in_project: Optional[str] = None
    is_active: Optional[bool] = None


class ProjectAssignmentResponse(ProjectAssignmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

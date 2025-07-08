# file: schemas/permission_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int

    class Config:
        from_attributes = True

# Role ke schema ko update karke usmein permissions dikhayenge
# Naya schema: Role with its permissions
class RoleWithPermissions(BaseModel):
    id: int
    name: str
    permissions: List[Permission] = []

    class Config:
        from_attributes = True

# Role ko permissions assign karne ke liye schema
class AssignPermissionsToRole(BaseModel):
    permission_ids: List[int] = Field(..., min_items=1)
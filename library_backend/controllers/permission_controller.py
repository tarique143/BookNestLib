# file: controllers/permission_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models import user_model, permission_model
from schemas import permission_schema
# get_current_admin_user ko hata kar require_permission ko import kiya gaya hai
from auth import require_permission, get_db
from utils import create_log # Logging ke liye import

router = APIRouter()

# --- Permissions Management ---

@router.post("/permissions", response_model=permission_schema.Permission, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("PERMISSION_MANAGE"))])
def create_permission(
    permission: permission_schema.PermissionCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("PERMISSION_MANAGE")) # Current user ko log karne ke liye
):
    """
    Ek nayi permission define karein (e.g., USER_MANAGE).
    """
    if db.query(permission_model.Permission).filter(permission_model.Permission.name == permission.name).first():
        raise HTTPException(status_code=409, detail="Permission with this name already exists")
    
    new_permission = permission_model.Permission(**permission.dict())
    db.add(new_permission)
    create_log(db, current_user, "PERMISSION_CREATED", f"Permission '{permission.name}' created.")
    db.commit()
    db.refresh(new_permission)
    return new_permission

@router.get("/permissions", response_model=List[permission_schema.Permission], dependencies=[Depends(require_permission("PERMISSION_VIEW"))])
def get_all_permissions(db: Session = Depends(get_db)):
    """
    System mein available sabhi permissions ki list dekhein.
    """
    return db.query(permission_model.Permission).all()

# --- Role and Permission Linking ---

@router.post("/roles/{role_id}/permissions", response_model=permission_schema.RoleWithPermissions, dependencies=[Depends(require_permission("ROLE_PERMISSION_ASSIGN"))])
def assign_permissions_to_role(
    role_id: int,
    assignment_data: permission_schema.AssignPermissionsToRole,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("ROLE_PERMISSION_ASSIGN"))
):
    """
    Ek role ko ek ya ek se zyada permissions assign karein.
    """
    db_role = db.query(user_model.Role).filter(user_model.Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
        
    permissions = db.query(permission_model.Permission).filter(permission_model.Permission.id.in_(assignment_data.permission_ids)).all()
    # set() ka istemal duplicate IDs ko handle karne ke liye
    if len(permissions) != len(set(assignment_data.permission_ids)):
        raise HTTPException(status_code=404, detail="One or more permission IDs are invalid or not found")
        
    db_role.permissions = permissions
    log_desc = f"Permissions {assignment_data.permission_ids} assigned to role '{db_role.name}'."
    create_log(db, current_user, "ROLE_PERMISSIONS_UPDATED", log_desc, "Role", role_id)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.get("/roles/{role_id}/permissions", response_model=permission_schema.RoleWithPermissions, dependencies=[Depends(require_permission("ROLE_VIEW"))])
def get_role_permissions(role_id: int, db: Session = Depends(get_db)):
    """
    Ek role ke paas kaun si permissions hain, woh dekhein.
    """
    db_role = db.query(user_model.Role).filter(user_model.Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role
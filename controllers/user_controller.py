# file: controllers/user_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import user_model
from schemas import user_schema
from utils import create_log
from auth import get_password_hash, require_permission, get_db

router = APIRouter()

@router.post("/roles", response_model=user_schema.Role, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("ROLE_MANAGE"))])
def create_role(
    role: user_schema.RoleCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("ROLE_MANAGE"))
):
    if db.query(user_model.Role).filter(user_model.Role.name == role.name).first():
        raise HTTPException(status_code=409, detail="Role with this name already exists")
    new_role = user_model.Role(name=role.name)
    db.add(new_role)
    create_log(db, current_user, "ROLE_CREATED", f"Role '{role.name}' created.")
    db.commit()
    db.refresh(new_role)
    return new_role

@router.get("/roles", response_model=List[user_schema.Role], dependencies=[Depends(require_permission("ROLE_VIEW"))])
def get_roles(db: Session = Depends(get_db)):
    return db.query(user_model.Role).all()

@router.post("/", response_model=user_schema.User, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("USER_MANAGE"))])
def create_user(
    user: user_schema.UserCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("USER_MANAGE"))
):
    if db.query(user_model.User).filter(user_model.User.email == user.email).first():
        raise HTTPException(status_code=409, detail="Email is already registered")
    if db.query(user_model.User).filter(user_model.User.username == user.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    
    hashed_password = get_password_hash(user.password)
    new_user = user_model.User(
        full_name=user.full_name, email=user.email, username=user.username,
        password_hash=hashed_password, role_id=user.role_id, status="Active"
    )
    db.add(new_user)
    create_log(db, current_user, "USER_CREATED", f"User '{user.username}' created.", "User", new_user.id)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/", response_model=List[user_schema.User], dependencies=[Depends(require_permission("USER_VIEW"))])
def get_users(db: Session = Depends(get_db)):
    return db.query(user_model.User).all()
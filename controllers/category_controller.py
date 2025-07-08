# file: controllers/category_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import book_model, user_model
from schemas import category_schema
from auth import require_permission, get_db
from utils import create_log

router = APIRouter()

@router.post("/", response_model=category_schema.Category, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("CATEGORY_MANAGE"))])
def create_category(
    category: category_schema.CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("CATEGORY_MANAGE"))
):
    if db.query(book_model.Category).filter(book_model.Category.name == category.name).first():
        raise HTTPException(status_code=409, detail="Category with this name already exists")
    
    new_category = book_model.Category(**category.dict())
    db.add(new_category)
    create_log(db, current_user, "CATEGORY_CREATED", f"Category '{category.name}' created.")
    db.commit()
    db.refresh(new_category)
    return new_category

# Public endpoint
@router.get("/", response_model=List[category_schema.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(book_model.Category).offset(skip).limit(limit).all()

# Public endpoint
@router.get("/{category_id}", response_model=category_schema.Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(book_model.Category).filter(book_model.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category
# --- UPDATE (Naya Function) ---
@router.put("/{category_id}", response_model=category_schema.Category, dependencies=[Depends(require_permission("CATEGORY_MANAGE"))])
def update_category(
    category_id: int, 
    category_update: category_schema.CategoryCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("CATEGORY_MANAGE"))
):
    db_category = db.query(book_model.Category).filter(book_model.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Update fields
    db_category.name = category_update.name
    db_category.description = category_update.description
    
    create_log(db, current_user, "CATEGORY_UPDATED", f"Category ID {category_id} updated.")
    db.commit()
    db.refresh(db_category)
    return db_category

# --- DELETE (Naya Function) ---
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("CATEGORY_MANAGE"))])
def delete_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("CATEGORY_MANAGE"))
):
    db_category = db.query(book_model.Category).filter(book_model.Category.id == category_id).first()
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    create_log(db, current_user, "CATEGORY_DELETED", f"Category '{db_category.name}' (ID: {category_id}) deleted.")
    db.delete(db_category)
    db.commit()
    return {"detail": "Category deleted successfully"} # Response 204 me body nahi jaati, par yeh confirmation ke liye hai
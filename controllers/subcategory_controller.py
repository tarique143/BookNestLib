# file: controllers/subcategory_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from models import book_model, user_model
from schemas import subcategory_schema
from auth import require_permission, get_db
from utils import create_log

router = APIRouter()

@router.post("/", response_model=subcategory_schema.Subcategory, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("CATEGORY_MANAGE"))])
def create_subcategory(
    subcategory: subcategory_schema.SubcategoryCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("CATEGORY_MANAGE"))
):
    if not db.query(book_model.Category).filter(book_model.Category.id == subcategory.category_id).first():
        raise HTTPException(status_code=404, detail=f"Parent category with id {subcategory.category_id} not found.")
    
    db_subcategory = book_model.Subcategory(**subcategory.dict())
    db.add(db_subcategory)
    create_log(db, current_user, "SUBCATEGORY_CREATED", f"Subcategory '{subcategory.name}' created.")
    db.commit()
    db.refresh(db_subcategory)
    return db_subcategory

# Public endpoint
@router.get("/", response_model=List[subcategory_schema.SubcategoryWithCategory])
def read_subcategories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(book_model.Subcategory).options(joinedload(book_model.Subcategory.category)).offset(skip).limit(limit).all()

# Public endpoint
@router.get("/{subcategory_id}", response_model=subcategory_schema.SubcategoryWithCategory)
def read_subcategory(subcategory_id: int, db: Session = Depends(get_db)):
    db_subcategory = db.query(book_model.Subcategory).options(joinedload(book_model.Subcategory.category)).filter(book_model.Subcategory.id == subcategory_id).first()
    if db_subcategory is None:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    return db_subcategory
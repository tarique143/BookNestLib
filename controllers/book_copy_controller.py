# file: controllers/book_copy_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from models import library_management_models as models, user_model
from schemas import library_management_schemas as schemas
from auth import require_permission, get_db
from utils import create_log

router = APIRouter()

@router.post("/", response_model=schemas.BookCopy, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("COPY_MANAGE"))])
def create_book_copy(
    copy: schemas.BookCopyCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("COPY_MANAGE"))
):
    db_copy = models.BookCopy(**copy.dict())
    db.add(db_copy)
    create_log(db, current_user, "COPY_CREATED", f"New copy created for Book ID {copy.book_id}.")
    db.commit()
    db.refresh(db_copy)
    return db_copy

@router.get("/", response_model=List[schemas.BookCopy], dependencies=[Depends(require_permission("COPY_VIEW"))])
def get_all_book_copies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.BookCopy).options(
        joinedload(models.BookCopy.book),
        joinedload(models.BookCopy.location)
    ).offset(skip).limit(limit).all()

@router.get("/{copy_id}", response_model=schemas.BookCopy, dependencies=[Depends(require_permission("COPY_VIEW"))])
def get_book_copy(copy_id: int, db: Session = Depends(get_db)):
    db_copy = db.query(models.BookCopy).filter(models.BookCopy.id == copy_id).first()
    if not db_copy:
        raise HTTPException(status_code=404, detail="Book copy not found")
    return db_copy
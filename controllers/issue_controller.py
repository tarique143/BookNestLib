# file: controllers/issue_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from models import library_management_models as models, user_model
from schemas import library_management_schemas as schemas
from auth import require_permission, get_db
from utils import create_log

router = APIRouter()

@router.post("/issue", response_model=schemas.IssuedBook, status_code=201, dependencies=[Depends(require_permission("BOOK_ISSUE"))])
def issue_book_to_client(
    issue_data: schemas.IssuedBookCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("BOOK_ISSUE"))
):
    db_copy = db.query(models.BookCopy).filter(models.BookCopy.id == issue_data.copy_id).first()
    if not db_copy:
        raise HTTPException(status_code=404, detail="Book copy not found")
    if db_copy.status != "Available":
        raise HTTPException(status_code=400, detail=f"Book copy is not available. Status: {db_copy.status}")
    
    db_issue = models.IssuedBook(**issue_data.dict())
    db_copy.status = "On Loan"
    
    db.add(db_issue)
    
    client = db.query(user_model.User).filter(user_model.User.id == issue_data.client_id).first()
    log_desc = f"Book copy ID {db_copy.id} issued to client '{client.username}'."
    create_log(db, current_user, "BOOK_ISSUED", log_desc, "IssuedBook", db_issue.id)
    
    db.commit()
    db.refresh(db_issue)
    return db_issue

@router.post("/return/{issue_id}", response_model=schemas.IssuedBook, dependencies=[Depends(require_permission("BOOK_ISSUE"))])
def return_book(
    issue_id: int, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("BOOK_ISSUE"))
):
    db_issue = db.query(models.IssuedBook).filter(models.IssuedBook.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue record not found")
    if db_issue.status == "Returned":
        raise HTTPException(status_code=400, detail="Book has already been returned")

    db_issue.status = "Returned"
    db_issue.actual_return_date = datetime.utcnow()
    
    db_copy = db.query(models.BookCopy).filter(models.BookCopy.id == db_issue.copy_id).first()
    if db_copy:
        db_copy.status = "Available"
    
    log_desc = f"Book copy ID {db_issue.copy_id} returned."
    create_log(db, current_user, "BOOK_RETURNED", log_desc, "IssuedBook", db_issue.id)

    db.commit()
    db.refresh(db_issue)
    return db_issue

@router.get("/", response_model=List[schemas.IssuedBook], dependencies=[Depends(require_permission("ISSUE_VIEW"))])
def get_all_issues(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.IssuedBook).offset(skip).limit(limit).all()
# file: controllers/request_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

from models import book_model, user_model, request_model
from schemas import request_schema
from auth import require_permission, get_db
from utils import create_log

router = APIRouter()

# --- Helper Function ---
def get_full_request_details(db: Session, request_id: int):
    """ Ek request ko uski sabhi nested details ke saath fetch karta hai. """
    return db.query(request_model.UploadRequest).options(
        joinedload(request_model.UploadRequest.book).joinedload(book_model.Book.language),
        joinedload(request_model.UploadRequest.book).joinedload(book_model.Book.subcategories),
        joinedload(request_model.UploadRequest.submitted_by).joinedload(user_model.User.role),
        joinedload(request_model.UploadRequest.reviewed_by).joinedload(user_model.User.role)
    ).filter(request_model.UploadRequest.id == request_id).first()

# --- CREATE ---
@router.post("/", response_model=request_schema.UploadRequest, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("REQUEST_CREATE"))])
def create_upload_request(
    request: request_schema.UploadRequestCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("REQUEST_CREATE"))
):
    """ Ek nayi book ke liye approval request create karein. """
    db_book = db.query(book_model.Book).filter(book_model.Book.id == request.book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if db.query(request_model.UploadRequest).filter(request_model.UploadRequest.book_id == request.book_id).first():
        raise HTTPException(status_code=409, detail="An upload request for this book already exists.")

    new_request = request_model.UploadRequest(
        book_id=request.book_id,
        submitted_by_id=current_user.id
    )
    db.add(new_request)
    db.flush() # ID generate karne ke liye
    create_log(db, current_user, "REQUEST_CREATED", f"Approval request for book ID {request.book_id} created.", "Request", new_request.id)
    db.commit()
    db.refresh(new_request)
    return get_full_request_details(db, new_request.id) # Poori details ke saath return karein

# --- READ (List) ---
@router.get("/", response_model=List[request_schema.UploadRequest])
def get_all_requests(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    """ Sabhi requests ki list fetch karein. """
    query = db.query(request_model.UploadRequest).options(
        joinedload(request_model.UploadRequest.book),
        joinedload(request_model.UploadRequest.submitted_by),
        joinedload(request_model.UploadRequest.reviewed_by)
    )
    if status_filter:
        query = query.filter(request_model.UploadRequest.status == status_filter)
    return query.order_by(request_model.UploadRequest.submitted_at.desc()).all()

# --- UPDATE (Review) ---
@router.put("/{request_id}/review", response_model=request_schema.UploadRequest, dependencies=[Depends(require_permission("REQUEST_APPROVE"))])
def review_upload_request(
    request_id: int,
    review_data: request_schema.ReviewRequest,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("REQUEST_APPROVE"))
):
    """ Ek request ko Approve ya Reject karein. """
    db_request = db.query(request_model.UploadRequest).filter(request_model.UploadRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if db_request.status != 'Pending':
        raise HTTPException(status_code=400, detail="This request has already been reviewed")
    
    db_request.status = review_data.status
    db_request.remarks = review_data.remarks
    db_request.reviewed_by_id = current_user.id
    db_request.reviewed_at = datetime.utcnow()
    
    if review_data.status == 'Approved':
        db_book = db.query(book_model.Book).filter(book_model.Book.id == db_request.book_id).first()
        if db_book:
            db_book.is_approved = True
    
    create_log(db, current_user, "REQUEST_REVIEWED", f"Request ID {request_id} was {review_data.status}.", "Request", request_id)
    db.commit()
    
    # Poori details ke saath updated request ko fetch karke return karein
    updated_request = get_full_request_details(db, request_id)
    return updated_request
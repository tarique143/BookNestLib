# file: controllers/book_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

# Sabhi zaroori models aur schemas
from models import book_model, language_model, user_model, book_permission_model
from schemas import book_schema

# Authentication aur helper functions
from auth import require_permission, get_db, get_current_user
from utils import create_log

router = APIRouter()

@router.get("/", response_model=List[book_schema.Book])
def read_books(
    skip: int = 0, limit: int = 100, 
    approved_only: bool = True, db: Session = Depends(get_db)
):
    """ Sabhi non-deleted books ki list fetch karein (sirf non-restricted). """
    query = db.query(book_model.Book).options(
        joinedload(book_model.Book.subcategories).joinedload(book_model.Subcategory.category),
        joinedload(book_model.Book.language)
    ).filter(
        book_model.Book.is_restricted == False,
        book_model.Book.deleted_at.is_(None)  # Soft Delete Filter
    )
    
    if approved_only:
        query = query.filter(book_model.Book.is_approved == True)
    
    books = query.offset(skip).limit(limit).all()
    return books

@router.get("/{book_id}", response_model=book_schema.Book)
def read_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[user_model.User] = Depends(get_current_user)
):
    """ Ek specific book ko uski ID se fetch karein, permission aur soft delete check ke saath. """
    db_book = db.query(book_model.Book).options(
        joinedload(book_model.Book.subcategories).joinedload(book_model.Subcategory.category),
        joinedload(book_model.Book.language)
    ).filter(
        book_model.Book.id == book_id,
        book_model.Book.deleted_at.is_(None) # Soft Delete Filter
    ).first()
    
    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if not db_book.is_approved:
        if not current_user or current_user.role.name.lower() != 'admin':
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found or not approved")

    if db_book.is_restricted:
        if not current_user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You must be logged in to view this restricted book.")
        
        if current_user.role.name.lower() == 'admin':
            return db_book

        permission_exists = db.query(book_permission_model.BookPermission).filter(
            book_permission_model.BookPermission.book_id == book_id,
            (book_permission_model.BookPermission.user_id == current_user.id) | 
            (book_permission_model.BookPermission.role_id == current_user.role_id)
        ).first()

        if not permission_exists:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to view this restricted book.")
    
    return db_book

@router.post("/", response_model=book_schema.Book, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("BOOK_MANAGE"))])
def create_book(
    book: book_schema.BookCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("BOOK_MANAGE"))
):
    """ Ek nayi book create karein. """
    if book.isbn and db.query(book_model.Book).filter(book_model.Book.isbn == book.isbn, book_model.Book.deleted_at.is_(None)).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"A book with ISBN {book.isbn} already exists.")
    
    if not db.query(language_model.Language).filter(language_model.Language.id == book.language_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Language with ID {book.language_id} not found.")
    
    subcategories = db.query(book_model.Subcategory).filter(book_model.Subcategory.id.in_(book.subcategory_ids)).all()
    if len(subcategories) != len(set(book.subcategory_ids)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more subcategories not found.")

    book_data = book.dict(exclude={"subcategory_ids"})
    db_book = book_model.Book(**book_data)
    db_book.subcategories = subcategories
    db_book.is_approved = False
    
    db.add(db_book)
    db.flush() # ID generate karne ke liye flush karein
    create_log(db, current_user, "BOOK_CREATED", f"Book '{book.title}' created and pending approval.", "Book", db_book.id)
    db.commit()
    db.refresh(db_book)
    return db_book

@router.put("/{book_id}", response_model=book_schema.Book, dependencies=[Depends(require_permission("BOOK_MANAGE"))])
def update_book(
    book_id: int,
    book_update: book_schema.BookCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("BOOK_MANAGE"))
):
    """ Ek maujooda book ko update karein. """
    db_book = db.query(book_model.Book).filter(
        book_model.Book.id == book_id,
        book_model.Book.deleted_at.is_(None)
    ).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = book_update.dict(exclude_unset=True)
    
    if "subcategory_ids" in update_data:
        subcategories = db.query(book_model.Subcategory).filter(book_model.Subcategory.id.in_(update_data["subcategory_ids"])).all()
        db_book.subcategories = subcategories
        del update_data["subcategory_ids"]
    
    for key, value in update_data.items():
        setattr(db_book, key, value)
    
    if hasattr(book_update, 'is_restricted'):
      db_book.is_restricted = book_update.is_restricted

    create_log(db, current_user, "BOOK_UPDATED", f"Book ID {book_id} was updated.")
    db.commit()
    db.refresh(db_book)
    return db_book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_permission("BOOK_MANAGE"))])
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("BOOK_MANAGE"))
):
    """ Ek book ko soft-delete karein. """
    db_book = db.query(book_model.Book).filter(
        book_model.Book.id == book_id,
        book_model.Book.deleted_at.is_(None)
    ).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db_book.deleted_at = datetime.utcnow()
    
    create_log(db, current_user, "BOOK_DELETED", f"Book '{db_book.title}' (ID: {book_id}) soft-deleted.")
    db.commit()
    # 204 response me body nahi hoti, isliye kuch return na karein ya ek empty response return karein
    return 
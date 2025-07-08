# file: schemas/request_schema.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .user_schema import User
from .book_schema import Book

class UploadRequestBase(BaseModel):
    book_id: int

class UploadRequestCreate(UploadRequestBase):
    pass

class ReviewRequest(BaseModel):
    status: str = Field(..., pattern="^(Approved|Rejected)$") # Sirf 'Approved' ya 'Rejected' allow karega
    remarks: Optional[str] = Field(None, max_length=500)

class UploadRequest(UploadRequestBase):
    id: int
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    remarks: Optional[str] = None
    submitted_by: Optional[User] = None
    reviewed_by: Optional[User] = None
    book: Book

    class Config:
        from_attributes = True
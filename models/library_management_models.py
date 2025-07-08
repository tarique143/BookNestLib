# file: models/library_management_models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, DateTime, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from .book_model import Book
from .user_model import User

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column("name", String(100), unique=True, nullable=False, index=True)
    room_name = Column("room_name", String(50), nullable=True)
    shelf_number = Column("shelf_number", String(20), nullable=True)
    section_name = Column("section_name", String(50), nullable=True)
    description = Column(String(255), nullable=True)
    book_copies = relationship("BookCopy", back_populates="location")

    # --- BADLAV YAHAN HAI ---
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    __table_args__ = {'mysql_engine': 'InnoDB'}

class BookCopy(Base):
    __tablename__ = "book_copies"
    id = Column("CopyID", Integer, primary_key=True, autoincrement=True)
    book_id = Column("BookID", Integer, ForeignKey("books.id"), nullable=False)
    location_id = Column("LocationID", Integer, ForeignKey("locations.id"), nullable=False)
    status = Column("Status", String(50), nullable=False, default="Available")
    book = relationship("Book")
    location = relationship("Location", back_populates="book_copies")
    issue_records = relationship("IssuedBook", back_populates="book_copy")

    # --- BADLAV YAHAN HAI ---
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    __table_args__ = {'mysql_engine': 'InnoDB'}

class IssuedBook(Base):
    __tablename__ = "issued_books"
    id = Column("IssuedBookID", Integer, primary_key=True, autoincrement=True)
    client_id = Column("ClientID", Integer, ForeignKey("users.ClientID"), nullable=False)
    copy_id = Column("CopyID", Integer, ForeignKey("book_copies.CopyID"), nullable=False)
    issue_date = Column("IssueDate", DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column("ReturnDate", DateTime, nullable=False)
    actual_return_date = Column("ActualReturnDate", DateTime, nullable=True)
    status = Column("Status", String(50), default="Issued")
    client = relationship("User")
    book_copy = relationship("BookCopy", back_populates="issue_records")
    
    # --- BADLAV YAHAN HAI ---
    # `issue_date` hi `created_at` ka kaam karega. Sirf `updated_at` add karte hain.
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = {'mysql_engine': 'InnoDB'}

class DigitalAccess(Base):
    __tablename__ = "digital_access"
    id = Column("DigitalAccessID", Integer, primary_key=True, autoincrement=True)
    client_id = Column("ClientID", Integer, ForeignKey("users.ClientID"), nullable=False)
    book_id = Column("BookID", Integer, ForeignKey("books.id"), nullable=False)
    access_granted = Column("AccessGranted", Boolean, default=True)
    # `access_timestamp` hi `created_at` ka kaam kar raha hai, isliye koi badlav nahi.
    access_timestamp = Column("AccessTimestamp", DateTime, default=datetime.utcnow, nullable=False)
    client = relationship("User")
    book = relationship("Book")
    
    __table_args__ = {'mysql_engine': 'InnoDB'}
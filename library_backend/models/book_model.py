# file: models/book_model.py
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Table, TIMESTAMP, DateTime, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

book_subcategory_link = Table(
    'book_subcategory_link', 
    Base.metadata,
    Column('book_id', Integer, ForeignKey('books.id', ondelete="CASCADE"), primary_key=True),
    Column('subcategory_id', Integer, ForeignKey('subcategories.id', ondelete="CASCADE"), primary_key=True),
    mysql_engine='InnoDB'
)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan")
    
    # --- BADLAV YAHAN HAI ---
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = {'mysql_engine': 'InnoDB'}

class Subcategory(Base):
    __tablename__ = "subcategories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    category = relationship("Category", back_populates="subcategories")
    books = relationship("Book", secondary=book_subcategory_link, back_populates="subcategories")

    # --- BADLAV YAHAN HAI ---
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = {'mysql_engine': 'InnoDB'}

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    author = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    publication_year = Column(Integer, nullable=True)
    isbn = Column(String(20), unique=True, index=True, nullable=True)
    language_id = Column(Integer, ForeignKey("languages.LanguageID", ondelete="SET NULL"), nullable=True)
    is_digital = Column(Boolean, default=False)
    cover_image_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=False)
    is_restricted = Column(Boolean, default=False)
    
    # --- BADLAV YAHAN HAI ---
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    language = relationship("Language", back_populates="books")
    subcategories = relationship("Subcategory", secondary=book_subcategory_link, back_populates="books")
    upload_request = relationship("UploadRequest", back_populates="book", cascade="all, delete-orphan", uselist=False)
    __table_args__ = {'mysql_engine': 'InnoDB'}
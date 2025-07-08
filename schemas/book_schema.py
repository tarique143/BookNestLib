# file: schemas/book_schema.py
from pydantic import BaseModel, Field
from typing import Optional, List
# Sahi language schema ko import kiya
from .language_schema import Language as LanguageSchema
# Sahi subcategory schema ko import kiya
from .subcategory_schema import SubcategoryWithCategory as SubcategorySchema

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    isbn: Optional[str] = Field(None, max_length=20)
    is_digital: bool = False
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    language_id: int

class BookCreate(BookBase):
    subcategory_ids: List[int] = []

class Book(BookBase):
    id: int
    is_approved: bool
    is_restricted: bool
    # Sahi schema ka istemal kiya
    language: LanguageSchema
    subcategories: List[SubcategorySchema] = []

    class Config:
        from_attributes = True
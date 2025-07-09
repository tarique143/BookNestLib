# file: controllers/language_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import language_model, user_model
from schemas import language_schema
from auth import require_permission, get_db
from utils import create_log

router = APIRouter()

@router.post("/", response_model=language_schema.Language, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("LANGUAGE_MANAGE"))])
def create_language(
    language: language_schema.LanguageCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("LANGUAGE_MANAGE"))
):
    if db.query(language_model.Language).filter(language_model.Language.name == language.name).first():
        raise HTTPException(status_code=409, detail="Language with this name already exists")
    
    new_language = language_model.Language(**language.dict())
    db.add(new_language)
    create_log(db, current_user, "LANGUAGE_CREATED", f"Language '{language.name}' created.")
    db.commit()
    db.refresh(new_language)
    return new_language

# Public endpoint
@router.get("/", response_model=List[language_schema.Language])
def read_languages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(language_model.Language).offset(skip).limit(limit).all()

# Public endpoint
@router.get("/{language_id}", response_model=language_schema.Language)
def read_language(language_id: int, db: Session = Depends(get_db)):
    db_language = db.query(language_model.Language).filter(language_model.Language.id == language_id).first()
    if db_language is None:
        raise HTTPException(status_code=404, detail="Language not found")
    return db_language
# file: controllers/location_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import library_management_models as models, user_model
from schemas import library_management_schemas as schemas
from auth import require_permission, get_db
from utils import create_log

router = APIRouter()

@router.post("/", response_model=schemas.Location, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_permission("LOCATION_MANAGE"))])
def create_location(
    location: schemas.LocationCreate, 
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("LOCATION_MANAGE"))
):
    if db.query(models.Location).filter(models.Location.name == location.name).first():
        raise HTTPException(status_code=409, detail=f"Location with name '{location.name}' already exists.")
    
    new_location = models.Location(**location.dict())
    db.add(new_location)
    create_log(db, current_user, "LOCATION_CREATED", f"Location '{location.name}' created.")
    db.commit()
    db.refresh(new_location)
    return new_location

# Public endpoint
@router.get("/", response_model=List[schemas.Location])
def get_all_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Location).offset(skip).limit(limit).all()
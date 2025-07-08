# file: controllers/log_controller.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from models import log_model
from schemas import log_schema
from auth import require_permission, get_db

router = APIRouter()

@router.get("/", response_model=List[log_schema.Log], dependencies=[Depends(require_permission("LOG_VIEW"))])
def get_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    action_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    System logs dekhein. Filters apply kar sakte hain.
    """
    query = db.query(log_model.Log).order_by(log_model.Log.timestamp.desc())
    if user_id:
        query = query.filter(log_model.Log.action_by_id == user_id)
    if action_type:
        query = query.filter(log_model.Log.action_type == action_type)
    
    logs = query.offset(skip).limit(limit).all()
    return logs
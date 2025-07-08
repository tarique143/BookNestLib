# file: schemas/log_schema.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .user_schema import User

class Log(BaseModel):
    id: int
    timestamp: datetime
    action_type: str
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    description: Optional[str] = None
    action_by: Optional[User] = None

    class Config:
        from_attributes = True
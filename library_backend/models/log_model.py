# file: models/log_model.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    # --- BADLAV YAHAN HAI (consistency ke liye) ---
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    action_by_id = Column(Integer, ForeignKey('users.ClientID'), nullable=True)
    action_type = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=True)
    target_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    action_by = relationship("User")
    __table_args__ = {'mysql_engine': 'InnoDB'}
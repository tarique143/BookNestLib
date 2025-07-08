# file: models/log_model.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
# User model ko yahan se import karne ke bajaye, hum string ka istemal karenge
# taaki circular dependency se bacha ja sake.
# from .user_model import User # Is line ko comment ya hata dein

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    
    # TIMESTAMP ko NOT NULL banaya aur timezone=True add kiya for consistency
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    
    action_by_id = Column(Integer, ForeignKey('users.ClientID'), nullable=True)
    action_type = Column(String(100), nullable=False)
    target_type = Column(String(50), nullable=True)
    target_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)

    # Relationship ko string ke zariye define karein
    action_by = relationship("User")
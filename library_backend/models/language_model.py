# file: models/language_model.py
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, DateTime, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Language(Base):
    __tablename__ = "languages"
    id = Column("LanguageID", Integer, primary_key=True, index=True)
    name = Column("LanguageName", String(100), unique=True, nullable=False, index=True)
    description = Column("Description", Text, nullable=True)
    books = relationship("Book", back_populates="language")

    # --- BADLAV YAHAN HAI ---
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    __table_args__ = {'mysql_engine': 'InnoDB'}
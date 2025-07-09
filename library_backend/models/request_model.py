# file: models/request_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

class UploadRequest(Base):
    __tablename__ = 'upload_requests'
    id = Column(Integer, primary_key=True, index=True)
    submitted_by_id = Column(Integer, ForeignKey('users.ClientID', ondelete="SET NULL"), nullable=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete="CASCADE"), nullable=False, unique=True)
    status = Column(SQLAlchemyEnum('Pending', 'Approved', 'Rejected', name='request_status_enum'), default='Pending', nullable=False)
    reviewed_by_id = Column(Integer, ForeignKey('users.ClientID', ondelete="SET NULL"), nullable=True)
    
    # --- BADLAV YAHAN HAI ---
    # submitted_at hi created_at ka kaam karega
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # reviewed_at hi updated_at ka kaam karega
    reviewed_at = Column(DateTime, nullable=True)
    
    remarks = Column(String(500), nullable=True)
    submitted_by = relationship("User", foreign_keys=[submitted_by_id])
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    book = relationship("Book", back_populates="upload_request", uselist=False)
    
    __table_args__ = {'mysql_engine': 'InnoDB'}
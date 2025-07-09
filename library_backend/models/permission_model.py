# file: models/permission_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, Table, TIMESTAMP, DateTime, func
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

role_permission_link = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete="CASCADE"), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete="CASCADE"), primary_key=True),
    mysql_engine='InnoDB'
)

class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    roles = relationship("Role", secondary=role_permission_link, back_populates="permissions")

    # --- BADLAV YAHAN HAI ---
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = {'mysql_engine': 'InnoDB'}
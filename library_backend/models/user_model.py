# file: models/user_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, func, TIMESTAMP, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from .permission_model import role_permission_link

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    users = relationship("User", back_populates="role")
    permissions = relationship("Permission", secondary=role_permission_link, back_populates="roles")

    # --- BADLAV YAHAN HAI ---
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = {'mysql_engine': 'InnoDB'}

class User(Base):
    __tablename__ = "users"
    id = Column("ClientID", Integer, primary_key=True, index=True)
    full_name = Column("FullName", String(255), nullable=True)
    email = Column("Email", String(255), unique=True, nullable=False, index=True)
    username = Column("Username", String(100), unique=True, nullable=False, index=True)
    password_hash = Column("PasswordHash", String(255), nullable=False)
    
    # --- BADLAV YAHAN HAI ---
    # date_joined ko created_at ki tarah treat karenge aur DateTime banayenge
    date_joined = Column("DateJoined", DateTime, default=datetime.utcnow, nullable=False)
    status = Column("Status", String(50), default="Active")
    role_id = Column("RoleID", Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users")

    # --- BADLAV YAHAN HAI ---
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    __table_args__ = {'mysql_engine': 'InnoDB'}
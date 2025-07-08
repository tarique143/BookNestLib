# file: database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Apne MySQL username aur password se isko badlein
DATABASE_URL = "mysql+mysqlconnector://root:root@localhost:3306/library_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
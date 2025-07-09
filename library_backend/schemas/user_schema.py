# file: schemas/user_schema.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import datetime

class RoleBase(BaseModel):
    name: str = Field(..., example="User")

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    # 'full_name' ko JSON mein 'fullName' se map karne ke liye alias istemal kiya
    full_name: Optional[str] = Field(None, alias="fullName")
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    role_id: int = Field(..., example=1)

class User(UserBase):
    id: int
    status: str
    date_joined: datetime.datetime
    role: Role

    class Config:
        from_attributes = True
        # Alias (jaise 'fullName') ko kaam karne ke liye yeh zaroori hai
        populate_by_name = True
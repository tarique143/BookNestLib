# file: controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from models import user_model
from auth import verify_password, create_access_token, get_db, ACCESS_TOKEN_EXPIRE_MINUTES
from utils import create_log

router = APIRouter()

@router.post("/token", tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(user_model.User).filter(user_model.User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        # Log failed login attempt
        create_log(db, None, "LOGIN_FAILED", f"Failed login attempt for username: {form_data.username}")
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != 'Active':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User account is inactive.")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.name}, expires_delta=access_token_expires
    )
    
    # Log successful login
    create_log(db, user, "LOGIN_SUCCESS", f"User '{user.username}' logged in successfully.")
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.name}
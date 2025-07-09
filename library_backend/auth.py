# file: auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session, joinedload
from models import user_model
from database import SessionLocal

SECRET_KEY = "this-is-a-very-secret-key-please-change-it-for-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- NAYA BADLAV YAHAN HAI ---
# auto_error=False ka matlab hai ki token na hone par error mat do
optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    # ... (yeh function waisa hi rahega)
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- NAYA BADLAV YAHAN HAI ---
# get_current_user function ko isse replace karein
async def get_current_user(token: str | None = Depends(optional_oauth2_scheme), db: Session = Depends(get_db)):
    if token is None:
        return None # Agar token nahi hai, toh koi user nahi hai

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(user_model.User).options(joinedload(user_model.User.role)).filter(user_model.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# require_permission function waisa hi rahega, kyunki woh get_current_user par depend karta hai
def require_permission(permission_name: str):
    async def permission_checker(
        current_user: user_model.User = Depends(get_current_user), # Yeh ab None bhi ho sakta hai
        db: Session = Depends(get_db)
    ):
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        if current_user.status != "Active":
             raise HTTPException(status_code=400, detail="Inactive user, please contact admin.")

        # ... (baaki ka permission check logic waisa hi rahega) ...
        user_with_role_and_permissions = db.query(user_model.User) \
            .options(joinedload(user_model.User.role).joinedload(user_model.Role.permissions)) \
            .filter(user_model.User.id == current_user.id).one_or_none()

        if not user_with_role_and_permissions or not user_with_role_and_permissions.role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User has no role assigned.")
        
        if user_with_role_and_permissions.role.name.lower() == 'admin':
            return user_with_role_and_permissions

        user_permissions = {p.name for p in user_with_role_and_permissions.role.permissions}
        if permission_name not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission_name}' required to perform this action."
            )
        
        return user_with_role_and_permissions
        
    return permission_checker
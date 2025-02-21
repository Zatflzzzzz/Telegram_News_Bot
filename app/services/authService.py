from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config.config import settings
from app.config.dependencies import get_db
from app.dto.dto import TokenDataDto
from app.entities.model import User
from app.services.newsService import json_response

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_user_by_username(
        db: Session,
        username: str):

    user = db.query(User).filter(User.username == username).first()

    if user:
        return user

    return None


def create_access_token(
        data: dict,
        expires_delta: timedelta = None):

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def authenticate_user(
        db: Session,
        username: str,
        password: str):

    user = get_user_by_username(db, username)

    if user and pwd_context.verify(password, user.password):
        return user

    return None

def create_user(
        db: Session,
        username: str,
        password: str):

    if db.query(User).filter(User.username == username).first():
        return json_response(False, "Username already exists")

    hashed_password = pwd_context.hash(password)

    db_user = User(username=username, password=hashed_password)

    db.add(db_user)
    db.commit()

    db.refresh(db_user)

    return json_response(True, "User created", {"id": db_user.id, "username": db_user.username})


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenDataDto(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=token_data.username)

    if user is None:
        raise credentials_exception
    return user
from datetime import datetime,timedelta,timezone
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.database import getdb
from app.models.user import User
SECRET_KEY="51bg5fg64b1s15sasdfafdsgfgbgf54as65d1f651ra"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10

pwd_context =CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password)->str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password)->bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data:dict)->str:
    to_encode =data.copy()
    expires=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expires})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        ALGORITHM
    )
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login/")


def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(getdb)):
    try:
        payload=jwt.decode(
            token,
            SECRET_KEY,
            ALGORITHM=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if  user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

        db_user=db.query(User).filter(User.id==user_id).first()

        if db_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not found")

        return db_user






    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid or expired token")












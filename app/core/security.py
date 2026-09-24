from datetime import datetime,timedelta,timezone
import jwt
import uuid
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import getdb
from app.models.user import User
SECRET_KEY="51bg5fg64b1s15sasdfafdsgfgbgf54as65d1f651ra"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS = 7

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
        algorithm=ALGORITHM
    )
oauth2_scheme = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
                     db:Session = Depends(getdb)):
    try:
        token = credentials.credentials
        payload=jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if  user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid token")

        db_user=db.query(User).filter(User.id==int(user_id)).first()

        if db_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="user not found")

        return db_user


    except jwt.InvalidTokenError as e:

        raise HTTPException(

            status_code=401,

            detail=str(e))

def create_refresh_token(data:dict)->str:
    toencode=data.copy()
    expires=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    toencode.update({"exp":expires,"type":"refresh","jti":str(uuid.uuid4())})

    return jwt.encode(
        toencode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )









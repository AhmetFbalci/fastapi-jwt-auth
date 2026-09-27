from datetime import datetime, timedelta, timezone
import jwt
import uuid
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import getdb
from app.models.user import User





# .env dosyasını yüklüyoruz.
load_dotenv()



SECRET_KEY = os.getenv("SECRET_KEY")


ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = 15

REFRESH_TOKEN_EXPIRE_DAYS = 7


GOOGLE_PENDING_TOKEN_EXPIRE_MINUTES = 5

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")




pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password) -> str:

    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:

    return pwd_context.verify(
        plain_password,
        hashed_password
    )




def create_access_token(data: dict) -> str:


    to_encode = data.copy()


    expires = (
        datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


    to_encode.update({
        "exp": expires
    })


    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ============================================================
# GOOGLE PENDING TOKEN
# ============================================================

def create_google_pending_token(data: dict) -> str:


    to_encode = data.copy()


    to_encode.update({
        "type": "google_pending"
    })


    expires = (
        datetime.now(timezone.utc)
        + timedelta(minutes=GOOGLE_PENDING_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({
        "exp": expires
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )




def create_refresh_token(data: dict) -> str:


    to_encode = data.copy()

    expires = (
        datetime.now(timezone.utc)
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )


    to_encode.update({
        "exp": expires,


        "type": "refresh",


        "jti": str(uuid.uuid4())
    })

    # JWT oluşturuyoruz.
    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )




oauth2_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(getdb)
):

    try:

        token = credentials.credentials


        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        # Kullanıcı ID yoksa token geçersiz.
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


        db_user = (
            db.query(User)
            .filter(User.id == int(user_id))
            .first()
        )


        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )


        return db_user

    except jwt.InvalidTokenError as e:


        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
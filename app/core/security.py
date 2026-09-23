from datetime import datetime,timedelta,timezone
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm.sync import update

SECRET_KEY="51bg5fg64b1s15sasdfafdsgfgbgf54as65d1f651ra"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10

pwd_context =CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password)->str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password)->bool:
    return pwd_context.context.verify(plain_password, hashed_password)

def create_access_token(data:dict)->str:
    to_encode =data.copy()
    expires=datetime.now(timezone.utc) + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode=update({"exp":expires})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        ALGORITHM
    )
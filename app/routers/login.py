from fastapi import  APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token,create_refresh_token,ALGORITHM,SECRET_KEY
from app.database import getdb
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.token import Token
from datetime import datetime, timezone
from app.models.refresh_token import RefreshToken
import jwt
router=APIRouter(
    prefix="/auth",
    tags=["auth"]
)
@router.post("/login",response_model=Token,status_code=200)
async def login(user:UserLogin,db:Session=Depends(getdb))->Token:
    try:
        db_user = db.query(User).filter(User.username == user.username).first()
        if not db_user:
            raise HTTPException(status_code=401,detail="username or password is wrong 1")

        password_correct=verify_password(user.password,db_user.password)

        if not password_correct:
            raise HTTPException(status_code=401,detail="username or password is wrong")

        access_token=create_access_token(
            {"sub":str(db_user.id),
            "username":db_user.username})

        refresh_token=create_refresh_token(
            {"sub":str(db_user.id)}
        )

        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        jti=payload["jti"]
        expires=datetime.fromtimestamp(payload["exp"],tz=timezone.utc)
        db_refresh_token = RefreshToken(
            token=jti,
            user_id=db_user.id,
            expires_at=expires,
            revoked=False
        )

        db.add(db_refresh_token)
        db.commit()
        return Token(access_token=access_token
                     ,refresh_token=refresh_token
                     ,token_type="bearer"
                     )

    except HTTPException:
        raise


    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))





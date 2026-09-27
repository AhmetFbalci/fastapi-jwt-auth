from fastapi import  APIRouter, HTTPException, Depends,status
from sqlalchemy.orm import Session
from app.core.security import hash_password,get_current_user, verify_password, create_access_token,create_refresh_token,ALGORITHM,SECRET_KEY
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




@router.post("/register",status_code=201,response_model=UserResponse)
def register(user:UserCreate,db:Session=Depends(getdb)):
    try:
        existing_user=db.query(User).filter((User.username==user.username)|(User.email==user.email)).first()
        if existing_user:
            raise HTTPException(status_code=400,detail="Username or email already exists")
        new_user=User(
            email=user.email,
            username=user.username,
            password=hash_password(user.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return  new_user

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt

from app.database import getdb
from app.models.refresh_token import RefreshToken
from app.core.security import SECRET_KEY, ALGORITHM




@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(getdb)):
    try:
        payload=jwt.decode(refresh_token,SECRET_KEY,algorithms=[ALGORITHM])
        if payload is None:
            raise HTTPException(status_code=401,detail="Invalid refresh token")
        jti=payload.get("jti")

        if jti is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        db_token=db.query(RefreshToken).filter(jti==RefreshToken.token).first()

        if db_token is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        db_token.revoked=True
        db.commit()

        return {
            "message":"Succesfully logged out"
        }


    except jwt.ExpiredSignatureError:
        raise HTTPException(
        status_code=401,
        detail="Refresh token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
        status_code=401,
        detail="Invalid refresh token"
        )



@router.post("/refresh")
async def refresh_access_token(refresh_token:str,db:Session=Depends(getdb)):
    try:
        payload=jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )



        if  payload.get("type")!="refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid refresh token ")



        jti = payload.get("jti")
        if jti is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )


        db_token = db.query(RefreshToken).filter(
            RefreshToken.token == jti
        ).first()

        if db_token is None:
            raise HTTPException(
                status_code=401,
                detail="Refresh token not found"
            )

        if db_token.revoked:
            raise HTTPException(
                status_code=401,
                detail="Refresh token revoked"
            )
        user_id=payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid refresh token ")


        access_token=create_access_token({
            "sub":user_id
        })


        return {
            "access_token":access_token,
            "token_type":"bearer"
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401,detail="Invalid refresh token")


@router.get("/me")
def get_me(current_user:User=Depends(get_current_user)):
    return current_user
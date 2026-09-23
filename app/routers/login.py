from fastapi import  APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token
from app.database import getdb
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin,Token

router=APIRouter(
    prefix="/login",
    tags=["login"]
)
@router.post("/",response_model=Token,status_code=200)
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

        return Token(access_token=access_token,token_type="bearer")
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))





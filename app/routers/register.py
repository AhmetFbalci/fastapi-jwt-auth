from fastapi import  APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.database import getdb
from app.models.user import User
from app.schemas.user import UserCreate,UserResponse

router=APIRouter(
    prefix="/auth",
    tags=["auth"]
)

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

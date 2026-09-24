from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt

from app.database import getdb
from app.models.refresh_token import RefreshToken
from app.core.security import SECRET_KEY, ALGORITHM


router=APIRouter(prefix="/auth",tags=["auth"])

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



from fastapi import APIRouter,HTTPException,status
import jwt
from app.core.security import ALGORITHM,SECRET_KEY,create_access_token
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import getdb
from app.models.refresh_token import RefreshToken


router =APIRouter(prefix="/auth",tags=["auth"])

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
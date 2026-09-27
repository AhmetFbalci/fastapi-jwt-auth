import jwt
from fastapi import APIRouter, HTTPException, Request  # HTTPException eklendi
from fastapi.params import Depends
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from app.schemas.token import Token
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.core.security import (create_access_token
,create_refresh_token, GOOGLE_CLIENT_SECRET
, create_google_pending_token, SECRET_KEY
, ALGORITHM,GOOGLE_CLIENT_ID)
from app.database import getdb
from datetime import timezone,datetime
from app.models.AuthAccount import AuthAccount

from sqlalchemy import select as Select

router = APIRouter(
    prefix="/auth",
    tags=["Google Authentication"]
)

oauth = OAuth()

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url=(
        "https://accounts.google.com/.well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile"
    }
)


@router.get("/google/login")
async def google_login(request: Request):
    try:
        print("LOGIN URL:", request.url)
        print("LOGIN SESSION BEFORE:", request.session)
        redirect_uri = request.url_for("google_callback")

        print("LOGIN SESSION AFTER:", request.session)
        return await oauth.google.authorize_redirect(
            request,
            redirect_uri
        )
        print("AFTER REDIRECT SESSION:", request.session)
    except Exception as e:
        print("GOOGLE LOGIN ERROR:", repr(e))

        raise HTTPException(
            status_code=400,
            detail=f"Google giriş yönlendirmesi başarısız oldu: {str(e)}"
        )


@router.get(
    "/google/callback",
    name="google_callback"
)
async def google_callback(request: Request, db: Session = Depends(getdb)):
    try:
        print("CALLBACK SESSION:", request.session)
        print("CALLBACK STATE:", request.query_params.get("state"))
        token = await oauth.google.authorize_access_token(request)

        user_info = token["userinfo"]
        google_id = user_info["sub"]
        email = user_info["email"]
        name = user_info["name"]

        google_account = db.scalar(
            Select(AuthAccount).where(
                AuthAccount.provider == "google",
                AuthAccount.provider_account_id == google_id
            )
        )
        if google_account:
            user = google_account.user

            access_token = create_access_token({
                "sub": str(user.id),
                "username": user.username
            })

            refresh_token = create_refresh_token({
                "sub": str(user.id)
            })

            payload = jwt.decode(
                refresh_token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            jti = payload["jti"]

            expires = datetime.fromtimestamp(
                payload["exp"],
                tz=timezone.utc
            )

            db_refresh_token = RefreshToken(
                token=jti,
                user_id=user.id,
                expires_at=expires,
                revoked=False
            )

            db.add(db_refresh_token)
            db.commit()

            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )

        pending_token = create_google_pending_token({
            "sub": google_id,
            "email": email,
            "name": name
        })

        return {
            "requires_username": True,
            "pending_token": pending_token
        }


    except Exception as e:

        print("GOOGLE CALLBACK ERROR:", repr(e))

        raise HTTPException(

            status_code=500,

            detail=f"Google callback error: {repr(e)}"

        )


@router.post("/google/complete")
async def complete_google_signup(
    username:str,
    pending_token:str,
    db:Session=Depends(getdb)
    ):
    try:
        payload=jwt.decode(
            pending_token,
            SECRET_KEY,algorithms=[ALGORITHM]
        )

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400,detail="Google kayıt tokenı geçersiz veya süresi dolmuş")

    if payload.get("type") !="google_pending":
        raise HTTPException(status_code=400,detail="Invalid token type")


    google_id = payload.get("sub")
    email = payload.get("email")


    if not google_id or not email:
        raise HTTPException(
            status_code=400,
            detail="Google kullanıcı bilgileri eksik"
        )

    existing_user = db.scalar(
        Select(User).where(
            User.username == username
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Bu username zaten kullanılıyor"
        )



    existing_google_account = db.scalar(
        Select(AuthAccount).where(
            AuthAccount.provider == "google",
            AuthAccount.provider_account_id == google_id
        )
    )

    user = User(
        username=username,
        email=email,
        password=None,
        is_active=True,
        is_superuser=False
    )

    db.add(user)
    db.flush()
    auth_account = AuthAccount(
        user_id=user.id,
        provider="google",
        provider_account_id=google_id,
        password_hash=None
    )
    db.add(auth_account)
    db.commit()
    access_token = create_access_token({
        "sub": str(user.id),
        "username": user.username
    })


    refresh_token = create_refresh_token({
        "sub": str(user.id)
    })


    payload = jwt.decode(
        refresh_token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    jti = payload["jti"]

    expires = datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc
    )


    db_refresh_token = RefreshToken(
        token=jti,
        user_id=user.id,
        expires_at=expires,
        revoked=False
    )

    db.add(db_refresh_token)


    db.commit()


    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
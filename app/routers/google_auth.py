
from fastapi import APIRouter, HTTPException, Request  # HTTPException eklendi
from fastapi.params import Depends
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session

from app.core.security import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET,create_google_pending_token
from app.database import getdb
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
        redirect_uri = request.url_for("google_callback")
        return await oauth.google.authorize_redirect(
            request,
            redirect_uri
        )
    except Exception as e:
        # OAuth yönlendirme hatası durumunda
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
            return {
                "message": "Existing Google user",
                "user_id": user.id
            }

        pending_token = create_google_pending_token({
            "sub": google_id,
            "email": email,
            "name": name
        })

        # Frontend'e Google ID'yi doğrudan vermiyoruz.
        return {
            "requires_username": True,
            "pending_token": pending_token
        }

    except Exception as e:
        # Token doğrulama, eksik anahtar (KeyError) veya veritabanı hatalarını yakalar
        raise HTTPException(
            status_code=400,
            detail=f"Google kimlik doğrulama işlemi başarısız: {str(e)}"
        )
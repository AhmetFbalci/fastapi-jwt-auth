
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.database import Base, engine

from app.routers.google_auth import router as google_login
from app.routers.auth import router as user_router
from app.core.security import SECRET_KEY

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)
app.include_router(user_router)

app.include_router(google_login)

Base.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Fastapi auth api"}


from fastapi import FastAPI
from app.database import Base, engine
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.routers.register import router as register
from app.routers.login import router as login
from app.routers.user_me import router as users_me
from app.routers.refresh import router as refresh
from app.routers.logout import router as logout
app = FastAPI()
app.include_router(register)
app.include_router(login)
app.include_router(users_me)
app.include_router(refresh)
app.include_router(logout)

Base.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Fastapi auth api"}


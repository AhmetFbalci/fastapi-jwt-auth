from fastapi import FastAPI
from app.database import Base, engine
#from app.models.user import User
from app.routers.auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)
Base.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Fastapi auth api"}


from fastapi import FastAPI
from app.database import Base, engine
#from app.models.user import User
from app.routers.register import router as register
from app.routers.login import router as login

app = FastAPI()
app.include_router(register)
app.include_router(login)
Base.metadata.create_all(engine)

@app.get("/")
async def root():
    return {"message": "Fastapi auth api"}


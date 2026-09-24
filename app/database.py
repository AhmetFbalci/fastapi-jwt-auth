import os
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker



BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

engine =create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
                      )

sessionlocal = sessionmaker(bind=engine)
Base = declarative_base()


def getdb():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()
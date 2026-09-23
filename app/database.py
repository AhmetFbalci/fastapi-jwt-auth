from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./users.db"

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
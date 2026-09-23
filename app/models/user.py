from sqlalchemy import Boolean, Integer, String, Column
from app.database import Base

class User(Base):
    __tablename__ = 'users'
    id  = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)


from sqlalchemy import Boolean, Integer, String, Column
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = 'users'
    id  = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(50), unique=True)
    password = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    auth_accounts = relationship(
        "AuthAccount",
        back_populates="user"
    )


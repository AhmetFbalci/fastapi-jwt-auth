from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship

class AuthAccount(Base):
    __tablename__="auth_accounts"
    id=Column(Integer,primary_key=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    provider=Column(String(50),nullable=False)
    provider_account_id = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=True)
    # Local girişte kullanıcının hashlenmiş şifresi burada tutulacak.
    # Google hesabında NULL olacak
    user = relationship(
        "User",
        back_populates="auth_accounts"
    )



from  pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    username:str
    email:EmailStr
    password:str


class UserResponse(BaseModel):
    username:str
    email:EmailStr
    password:str
    is_active:bool
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username:str
    password:str


class Token(BaseModel):
    access_token:str
    token_type:str
from pydantic import BaseModel,EmailStr
from typing_extensions import Literal

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserRead(BaseModel):
    name:str
    email:str
    org:str
    role:str

    class Config:
        orm_mode=True

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    org : str
    role : Literal['bank','coperate','auditor','admin']

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ActionRequest(BaseModel):
    doc_id:int
    action:str
from pydantic import BaseModel

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    org: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str
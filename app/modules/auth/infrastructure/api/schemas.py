from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class SesionResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
from typing import Optional
from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token : str
    token_type  : str

class RefreshRequest(BaseModel):
    refresh_token : str

class UserLogin(BaseModel):
    email:str
    password:str

class UserPublic(BaseModel):
    id : int
    email : str
    name : Optional[str] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None
    class Config:
        from_attributes = True

class ResetPassword(BaseModel):
    current_password:str
    new_password:str

class ForgotPass(BaseModel):
    email:str

class SetPassword(BaseModel):
    code:str
    new_password:str

class AddPassword(BaseModel):
    new_password:str





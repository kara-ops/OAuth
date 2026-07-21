from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

class TokenResponse(BaseModel):
    access_token : str
    token_type  : str

class RefreshRequest(BaseModel):
    refresh_token : str

class UserLogin(BaseModel):
    email : str
    password : str

class UserPublic(BaseModel):
    id : int
    email : str
    name : Optional[str] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None
    class Config:
        from_attributes = True

class UserSessionModel(BaseModel):
    id : int
    user_id : int
    session_id : uuid

    r_token_hash : str
    revoked_at : datetime
    
    device_name : str | None
    device_type : str | None
    browser : str | None
    os : str | None

    ip_address : str
    user_agent : str

    created_at : datetime
    expires_at : datetime
    last_seen : datetime

    auth : "UserAuthModel" | None
    user : "UserModel" | None





class UserAuthModel(BaseModel):
    id : int
    user_id : int 
    provider : str
    provider_id : str | None
    hashed_password : str | None
    create_at : datetime

    user : "UserModel" | None
    session : UserSessionModel | None


class UserModel(BaseModel):
    id : int
    email : str
    name : str | None
    is_active : bool
    create_at : datetime
    avtar_url : str | None

    auth : UserAuthModel | None
    session : UserSessionModel | None

UserAuthModel.model_rebuild()
UserSessionModel.model_rebuild()
UserModel.model_rebuild()


class ResetPassword(BaseModel):
    current_password : str
    new_password : str

class ForgotPass(BaseModel):
    email : str

class SetPassword(BaseModel):
    code : str
    new_password : str

class AddPassword(BaseModel):
    new_password : str





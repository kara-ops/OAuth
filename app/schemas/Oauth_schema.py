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
    name : str
    class Config:
        from_attributes = True





from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException
from app.core.config import settings
from datetime import timedelta, datetime, timezone

from uuid import uuid4



def create_access_token(user_id:int,sid:str)->str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    current = datetime.now(timezone.utc)
    jti = str(uuid4())
    payload = {
        "exp":expire,
        "iat":current,
        "jti" : jti,
        "sid":sid,
        "type" : "access",
        "sub" : str(user_id)

    }
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def create_refresh_token(user_id:int,sid:str)->str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    current = datetime.now(timezone.utc)
    jti = str(uuid4())

    payload = {
        "exp": expire,
        "iat":current,
        "sid":sid,
        "type": "refresh",
        "sub": str(user_id),
        "jti": jti
    }
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)


def decode_token(token:str)->dict:
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=settings.ALGORITHM)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code = 401, detail = "Expired Token"
        )
    except JWTError:
        raise HTTPException(
            status_code = 401, detail = "Invalid token"
        )


    
    





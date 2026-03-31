from fastapi import APIRouter,Depends, Header, HTTPException 
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.database.postgres import get_db
from app.utils import oauth_client 
from app.services import auth_service 
from app.core import security 
from datetime import datetime, timezone
from app.services import token_service 
from app.schemas.Oauth_schema import RefreshRequest, TokenResponse

router = APIRouter(prefix="/auth/google", tags =["auth"])

@router.get("/login")
def google_login():
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
    )
    return RedirectResponse(url)

@router.get("/callback")
#oauth_client = oc, auth_service = a, security = s, oauth_schema = os
async def google_callback(code:str, db:Session = Depends(get_db)):
    try:
        access_token = await oauth_client.exchange_code_for_token(code)
        print("access_token : ", access_token)
    except Exception as e:
        print("error:", e)
        raise

    
    get_user_data = await oauth_client.get_google_user(access_token)
    user_info = get_user_data

    get_or_create = auth_service.get_or_create_user(db=db,google_user=user_info)

    create_access =security.create_access_token(get_or_create.id)
    create_refresh = security.create_refresh_token(get_or_create.id)

    token_service.store_refresh_token(get_or_create.id, create_refresh)
    return TokenResponse(access_token=create_access,refresh_token=create_refresh,token_type="bearer")


@router.post("/refresh", response_model = TokenResponse )
def refresh_logic(request:RefreshRequest):
    decode_token = security.decode_token(request.refresh_token)

    if decode_token["type"] != "refresh":
        raise HTTPException(
            status_code = 401,
            detail = "Invalid token"
        )
    
    verify = token_service.verify_refresh_token(decode_token["sub"],request.refresh_token)
    if not verify:
        raise HTTPException(
            status_code = 401, 
            detail = "Invalid token"
        )
    
    token_service.delete_refresh_token(decode_token["sub"])

    create_refresh = security.create_refresh_token(int(decode_token["sub"]))
    create_access = security.create_access_token(int(decode_token["sub"]))

    token_service.store_refresh_token(decode_token["sub"], create_refresh)

    return TokenResponse(access_token=create_access, refresh_token=create_refresh,token_type="bearer")

@router.post("/logout")
def logout(authorization: str = Header()):
    try:
        scheme,access = authorization.split()
        if scheme.lower() != "bearer":
            raise Exception()
    except ValueError:
        raise HTTPException(
            status_code = 401,
            detail = "Invalid token"
        )
    
    decode = security.decode_token(access)
    if decode["type"] != "access":
        raise HTTPException(
            status_code = 401,
            detail = "Invalid token"
        )

    remain_ttl = int(decode["exp"] - datetime.now(timezone.utc).timestamp())
    if remain_ttl <0:
        remain_ttl = 0
    token_service.blacklist_token(decode["jti"],remain_ttl)

    token_service.delete_refresh_token(decode["sub"])
    return {
        "message":"logged out"
    }

    









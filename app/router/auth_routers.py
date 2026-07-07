from fastapi import APIRouter,Depends, Header, HTTPException, Request, Response
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.database.postgres import get_db
from app.utils import oauth_client 
from app.services import auth_service 
from app.core import security 
from datetime import datetime, timezone
from app.services import token_service 
from app.models.user_model import User
from app.schemas.Oauth_schema import RefreshRequest, TokenResponse, UserPublic, UserLogin, ResetPassword, ForgotPass, SetPassword
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags =["auth"])

@router.get("/oauth")
def google_login(request : Request)->str:
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.client.host

    call = token_service.rate_limiter(ip)
    if not call:
        raise HTTPException(
            status_code = 429, detail = "Too many request"
        )

    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
    )
    return RedirectResponse(url)

@router.get("/google/callback")
#oauth_client = oc, auth_service = a, security = s, oauth_schema = os
async def google_callback(res:Response,code:str, db:Session = Depends(get_db)):
    try:
        access_token = await oauth_client.exchange_code_for_token(code)
        print("access_token : ", access_token)
    except Exception as e:
        raise

    
    get_user_data = await oauth_client.get_google_user(access_token)
    user_info = get_user_data

    get_or_create = auth_service.get_or_create_user(db=db,google_user=user_info)

    create_access =security.create_access_token(get_or_create.id)
    create_refresh = security.create_refresh_token(get_or_create.id)

    token_service.store_refresh_token(get_or_create.id, create_refresh)
    res.set_cookie(
        key="refresh",
        value=create_refresh,
        max_age=60*60*24*7,
        samesite="lax",
        httponly=True,
        secure=True
    )

    return TokenResponse(access_token=create_access,token_type="bearer")


@router.post("/refresh", response_model = TokenResponse )
def refresh_logic(req:Request,res:Response):
    refresh_token = req.cookies.get("refresh")
    decode_token = security.decode_token(refresh_token)

    if decode_token["type"] != "refresh":
        raise HTTPException(
            status_code = 401,
            detail = "Invalid token"
        )
    
    verify = token_service.verify_refresh_token(decode_token["sub"],refresh_token)
    if not verify:
        raise HTTPException(
            status_code = 401, 
            detail = "Invalid token"
        )
    
    token_service.delete_refresh_token(decode_token["sub"])

    create_refresh = security.create_refresh_token(int(decode_token["sub"]))
    create_access = security.create_access_token(int(decode_token["sub"]))

    token_service.store_refresh_token(decode_token["sub"], create_refresh)
    res.set_cookie(
        key="refresh",
        max_age=60*60*24*7,
        value=create_refresh,
        secure=True,
        samesite="lax",
        httponly=True,
        )



    return TokenResponse(access_token=create_access,token_type="bearer")

@router.post("/logout")
def logout(res:Response,authorization: str = Header()):
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
    res.delete_cookie("refresh")
    return {
        "message":"logged out"
    }

@router.post("/login")
def local_login(res:Response,user:UserLogin,db:Session=Depends(get_db)):
    login = auth_service.login_l_user(user.email,user.password,db)
    access = security.create_access_token(login.id)
    refresh = security.create_refresh_token(login.id)
    res.set_cookie(
        key="refresh",
        value=refresh,
        max_age=60*60*24*7,
        samesite="lax",
        httponly=True,
        secure=True
    )
    return {"access_token":access,"token_type":"bearer"}

@router.post("/create_user")
def create_local_user(res:Response,user:UserLogin,db:Session=Depends(get_db)):
    create = auth_service.create_l_user(user.email,user.password,db)
    access = security.create_access_token(create.id)
    refresh = security.create_refresh_token(create.id)
    res.set_cookie(
        key="refresh",
        value=refresh,
        max_age=60*60*24*7,
        samesite="lax",
        httponly=True,
        secure=True

    )
    return {"access_token":access,"type":"bearer"}
    


@router.patch("/reset_password")
def reset_password(user:ResetPassword,db:Session=Depends(get_db),auth:User=Depends(get_current_user)):
    call_func = auth_service.reset_pass(auth.id,user.new_password,user.current_password,db)
    return call_func


@router.post("/forgot_password")
def forgot_pass(user:ForgotPass,db:Session=Depends(get_db)):
    return auth_service.forgot_password(user.email,db)

@router.patch("/set_password")
def set_password(token:str,user:SetPassword,db:Session=Depends(get_db)):
    call_func = auth_service.new_password(user.code,user.new_password,db,token)
    return call_func


    









from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.database.postgres import get_db
from app.utils import oauth_client as oc
from app.services import auth_service as a
from app.core import security as s
from app.schemas import Oauth_schema as ons
from app.services import token_service as ts


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
        access_token = await oc.exchange_code_for_token(code)
        print("access_token : ", access_token)
    except Exception as e:
        print("error:", e)
        raise

    
    get_user_data = await oc.get_google_user(access_token)
    user_info = get_user_data

    get_or_create = a.get_or_create_user(db=db,google_user=user_info)

    create_access =s.create_access_token(get_or_create.id)
    create_refresh =s.create_refresh_token(get_or_create.id)

    ts.store_refresh_token(get_or_create.id, create_refresh)
    return ons.TokenResponse(access_token=create_access,refresh_token=create_refresh,token_type="bearer")







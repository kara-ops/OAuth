from fastapi import Depends,HTTPException, Header

from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy import select

from app.database.postgres import get_db

from app.core.security import decode_token

from app.services.token_service import is_blacklisted

from app.models.user_model import User

from app.schemas.Oauth_schema import UserBaseModel

async def get_current_user(access:str, db:Session = Depends(get_db)):

    decode = decode_token(access)
    if decode["type"] != "access":
        raise HTTPException(
            status_code = 401,
            detail = "Invalid token"
        )
    
    if is_blacklisted(decode["jti"]):
        raise HTTPException(
            status_code = 401,
            detail = "Token revoked"
        )
    
    check = await db.execute(select(User).where(User.id==int(decode["sub"])))
    querry = check.scalar_one_or_none()
    if not querry:
        raise HTTPException(
            status_code = 401,
            detail = "User not found"
        )
    return UserBaseModel.model_validate(querry)

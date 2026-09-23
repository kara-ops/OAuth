from fastapi import Depends,HTTPException, Header

from sqlalchemy.ext.asyncio import AsyncSession as Session
from sqlalchemy import select

from app.database.postgres import get_db

from app.core.security import decode_token

from app.services.token_service import get_user,cache_my_user

from app.models.user_model import User

from app.schemas.Oauth_schema import UserBaseModel

import logging 

logger = logging.getLogger(__name__)

async def get_current_user(authorization: str = Header(), db:Session = Depends(get_db)):
    if not authorization:
        logger.warning("Token missing")
        raise HTTPException(
            status_code = 401, detail = "Header missing"
        )
    
    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"Token is not in bearer format : {parts}")
        raise HTTPException(
            status_code = 401, detail = "Invalid token format"
        )
    
    access = parts[1]

    decode = decode_token(access)
    if decode["type"] != "access":
        logger.warning(f"Invalid token type : {decode["type"]}")
        raise HTTPException(
            status_code = 401,
            detail = "Invalid token"
        )

    user_data = await get_user(decode["sub"])
    if user_data:
        logger.info(f"User data found in cache user_id : {decode["sub"]} : session_id : {decode["sid"]}: data : {user_data}")
        return {"user":UserBaseModel.model_validate_json(user_data),
                "payload":decode}
    
    check = await db.execute(select(User).where(User.id==int(decode["sub"])))
    querry = check.scalar_one_or_none()
    if not querry:
        logger.warning(f"User not found : {decode["sub"]}")
        raise HTTPException(
            status_code = 401,
            detail = "User not found"
        )
    user = UserBaseModel.model_validate(querry)
    await cache_my_user(decode["sub"],user)
    logger.info(f"User data cached : {user} : ttl : 1hr : cache_key : {decode["sub"]}")
    logger.info(f"User {user.id} email : {user.email} completed the request")
    return {"user":user,
            "payload":decode}

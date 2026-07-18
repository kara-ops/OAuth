from sqlalchemy.orm import Session,joinedload
from app.models.user_model import User,UserAuth,UserSession
from fastapi import Request,HTTPException

from app.utils.hashing import hash_password,verify_password
from app.utils.code_gen import gen_code,gen_url_token,get_uuid,user_agent_parse,sha_hash
from app.utils.email_service import forgot_pass_mail
from app.utils.time_calc import c_plus_d,current_time


from app.services.token_service import forgot_pass_key,get_forgot_pass_key,del_forgot_pass_key

from app.core.security import create_access_token,create_refresh_token,decode_token,decode_token_r


def get_or_create_user(db:Session, google_user:dict,ip:str,user_agent:str)->User:
    email = db.query(User).filter(User.email==google_user["email"]).options(joinedload(User.auth)).first()
    if email:

        provider = None
        for auth in email.auth:
            if auth.provider == "google":
                provider = "google"

        if provider == "google":

            uuid_code = get_uuid()
            expire = c_plus_d(7)
            create_r = create_refresh_token(email.id,uuid_code)
            hash_r = sha_hash(create_r)
            ua_parse = user_agent_parse(user_agent)

            add_s = UserSession(
                session_id = uuid_code,
                user_id = email.id,

                r_token_hash = hash_r,

                device_type = ua_parse["device_type"],
                device_name = ua_parse["device"],
                browser = ua_parse["browser"],
                os = ua_parse["os"],

                ip_address = ip,
                user_agent = user_agent,

                expires_at = expire
            )
            try:
               db.add(add_s)
               db.commit()
               db.refresh(add_s)
            except:
                db.rollback()
                raise
            return {"user":email,
                    "refresh":create_r,
                    "access":create_access_token(email.id,uuid_code)
                    }
        else:
            create_user = UserAuth(
                user_id = email.id,
                provider = "google",
                provider_id = google_user["id"]
            )
            email.avatar_url = google_user["picture"]
            email.name = google_user["name"]
            
            uuid_code = get_uuid()
            expire = c_plus_d(7)
            create_r = create_refresh_token(email.id,uuid_code)
            hash_r = sha_hash(create_r)
            ua_parse = user_agent_parse(user_agent)

            add_s = UserSession(
                session_id = uuid_code,
                user_id = email.id,

                r_token_hash = hash_r,

                device_type = ua_parse["device_type"],
                device_name = ua_parse["device"],
                browser = ua_parse["browser"],
                os = ua_parse["os"],

                ip_address = ip,
                user_agent = user_agent,

                expires_at = expire
            )
            try:
               db.add(create_user)
               db.add(add_s)
               db.commit()
               db.refresh(create_user)
            except:
                db.rollback()
                raise
            return {"user":email,
                    "refresh":create_r,
                    "access":create_access_token(email.id,uuid_code)
                    }
    else:
        user = User(
            email = google_user["email"],
            name = google_user["name"],
            avatar_url = google_user["picture"],
        )
        db.add(user)
        db.flush()

        user_auth = UserAuth(
            provider = "google",
            provider_id = google_user["id"],
            user_id = user.id
        )

        uuid_code = get_uuid()
        expire = c_plus_d(7)
        create_r = create_refresh_token(email.id,uuid_code)
        hash_r = sha_hash(create_r)
        ua_parse = user_agent_parse(user_agent)

        add_s = UserSession(
                session_id = uuid_code,
                user_id = user.id,

                r_token_hash = hash_r,

                device_type = ua_parse["device_type"],
                device_name = ua_parse["device"],
                browser = ua_parse["browser"],
                os = ua_parse["os"],

                ip_address = ip,
                user_agent = user_agent,

                expires_at = expire
            )
        try:
            db.add(add_s)
            db.add(user)
            db.add(user_auth)
            db.commit()
            db.refresh(user)
        except:
            db.rollback()
            raise
        return {"user":email,
                "refresh":create_r,
                "access":create_access_token(email.id,uuid_code)
                }
    
def create_l_user(ip,user_agent:str,email_id:str,password:str,db:Session):
    email = db.query(User).filter(User.email==email_id).first()  #db search for user exist or not

    if email:
        raise HTTPException(status_code=400,detail="Email already registered")

    
    create = User(
        email = email_id
    )

    db.add(create)
    db.flush()
    
    expiry = c_plus_d(7) # current time + given days

    ua_parsed = user_agent_parse(user_agent)
    hash_pass = hash_password(password)
    uuid_code = get_uuid()

    # create auth  tokens
    access = create_access_token(create.id,uuid_code)
    refresh = create_refresh_token(create.id,uuid_code)
    hash_r = sha_hash(refresh)


    add_s = UserSession(

        session_id = uuid_code,
        user_id = create.id,

        r_token_hash = hash_r,

        device_type = ua_parsed["device_type"],
        device_name = ua_parsed["device"],
        browser = ua_parsed["browser"],
        os = ua_parsed["os"],

        ip_address = ip,
        user_agent = user_agent,
        
        expires_at = expiry
        
        )
    
    db.add(add_s)


    auth = UserAuth(
        provider = "local",
        user_id = create.id,
        hashed_password=hash_pass
    )

    try:
        db.add(auth)
        db.commit()
    except:
        db.rollback()
        raise

    return {"refresh":refresh,
            "access":access,
            "user":create}

def login_l_user(ip:str,user_agent:str,email_id:str,password:str,db:Session):
    email = db.query(User).filter(User.email==email_id).options(joinedload(User.auth)).first()
    if not email:
        raise HTTPException(status_code=400,detail="Wrong credentials")

    for auth in email.auth:
        provider = None
        hashed_password = auth.hashed_password
        if auth.provider == "local":
            provider = "local"
    if not provider:
        raise HTTPException(status_code=400,detail="Wrong credentials")
    
    if not verify_password(password,hashed_password):
        raise HTTPException(status_code=400,detail="Wrong credentials")
    


    uuid_code = get_uuid()
    create_refresh = create_refresh_token(email.id,uuid_code)
    refresh_hash = sha_hash(create_refresh)
    ua_parse = user_agent_parse(user_agent)
    expire = c_plus_d(7)
    
    auth_s = UserSession(
        session_id = uuid_code,
        user_id = email.id,

        r_token_hash = refresh_hash,

        device_type = ua_parse["device_type"],
        device_name = ua_parse["device"],
        browser = ua_parse["browser"],
        os = ua_parse["os"],

        ip_address = ip,
        user_agent = user_agent,
        
        expires_at = expire
        
    )
    try:
        db.add(auth_s)
        db.commit()
        create_access = create_access_token(email.id,uuid_code)
    except:
        db.rollback()
        raise
    
    return {"user":email,
            "access":create_access,
            "refresh":create_refresh}

def login_g_user(req:Request,ip:str,user_agent:str,google_user:dict,db:Session):
    check = db.query(User).filter(User.email==google_user["email"]).option(joinedload(UserAuth)).first()
    if check:
        provider = None
        for auth in check.auth:
            if auth.provider == "google":
                provider = "google"
        if provider == "google":
            return {"user":check,
                    "refresh":"token",
                    "access":"token"}
        else:
            g_user = UserAuth(
                provider = "google",
                provider_id = google_user["id"],
                user_id = check.id     
            )
            check.avatar_url = google_user["picture"]
            

    ua_parsed = user_agent_parse(user_agent)
    uuid_code = get_uuid()
    create_refresh = create_refresh_token()


#change a password
def reset_pass(user_id:int,new_password:str,current_password:str,db:Session):
    if current_password == new_password:
        raise HTTPException(status_code=400,detail="new password cannot be same as current one")
    
    check = db.query(User).filter(User.id==user_id).first()
    if not check:
        raise HTTPException(status_code=400,detail="User does not exist")
    
    auth_check = db.query(UserAuth).filter(UserAuth.user_id==user_id,UserAuth.provider=="local").first()

    if not auth_check:
        raise HTTPException(status_code=400,detail="login with email password first")
    
    new_pass = hash_password(new_password)

    if not verify_password(current_password,auth_check.hashed_password):
        raise HTTPException(status_code=400,detail="incorrect current password")
    
    try:
       auth_check.hashed_password=new_pass

       db.commit()
    except:
        db.rollback()
        raise

    return {"successfully changed"}

# password forgotten
def forgot_password(email:str,db:Session):
    check = db.query(UserAuth).join(User).filter(User.email==email,UserAuth.provider=="local").first()
    if not check:
        return {"If an account exists, we've sent you instructions"}
    
    code = gen_code()  #generate a unique code
    url_token = gen_url_token()  #generate token for the url

    set_code = forgot_pass_key(url_token,check.user_id,code)  #code is joint with

    mail = forgot_pass_mail(code,f"http://127.0.0.1:8000/auth/set_password?token={url_token}")

    return {"If an account exists, we've sent you instructions"}



def new_password(code:str,password:str,db:Session,token:str):
    user_id = get_forgot_pass_key(token,code)
    if user_id is None:
        raise HTTPException(status_code=400,detail="Invalid or expired code")

    new_pass = hash_password(password)

    check = db.query(UserAuth).filter(UserAuth.user_id==user_id,UserAuth.provider=="local").first()

    try:

        check.hashed_password=new_pass

        db.commit()

        redis_call = del_forgot_pass_key(token,code)
    except:
        db.rollback()
        raise
    
    return {"Password changed successfully"}


# add password to existing google email
def add_password(user_id:int,password:str,db:Session):
    check = db.query(UserAuth).filter(UserAuth.user_id==user_id,UserAuth.provider=="local").first()
    if check is not None:
        raise HTTPException(status_code=400,detail="This email has a password, to change password use forgot-password or resent password")
    
    hash_pass = hash_password(password)

    add_auth = UserAuth(
        user_id = user_id,
        provider = "local",
        hashed_password = hash_pass
    )
    try:
        db.add(add_auth)
        db.commit()
    except:
        db.rollback()
        raise
    return {"Password added successfully"}

def get_session(user_id:int,db:Session):
    get = db.query(UserSession.last_seen,UserSession.device_type,UserSession.device_name).filter(UserSession.user_id==user_id).all()
    if get is None:
        raise HTTPException(status_code=400,detail="No session's found")

    session = [dict(row._mapping) for row in get]
    return session

def refresh_token(token:str,db:Session):
    token = decode_token_r(token,db)

    get = db.query(UserSession).filter(UserSession.session_id==token["sid"]).first()
    if get is None:
        raise HTTPException(status_code=400,detail="Session not found")
    
    new_r = create_refresh_token(token["sub"],token["sid"])
    new_r_hash = sha_hash(new_r)
    new_a = create_access_token(token["sub"],token["sid"])

    get.r_token_hash = new_r_hash
    get.last_seen = current_time()
    get.expires_at = c_plus_d(7)
    get.created_at = current_time()
    try:
        db.commit()
    except:
        db.rollback()
        raise
    return {"refresh":new_r,
            "access":new_a,
            "sub":token["sub"]}
    
    

    


    

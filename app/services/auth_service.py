from sqlalchemy.orm import Session
from app.models.user_model import User,UserAuth
from fastapi import Request,HTTPException
from app.utils.hashing import hash_password,verify_password
from app.utils.code_gen import gen_code,gen_url_token
from app.services.token_service import forgot_pass_key,get_forgot_pass_key,del_forgot_pass_key
from app.utils.email_service import forgot_pass_mail

def get_or_create_user(db:Session, google_user:dict)->User:
    email = db.query(User).filter(User.email==google_user["email"]).first()
    if email:
        check = db.query(UserAuth).filter(UserAuth.user_id==email.id).first()
        if check:
            return email
        else:
            create_user = UserAuth(
                user_id = email.id,
                provider = "google",
                provider_id = google_user["id"]
            )
            email.avatar_url = google_user["picture"]
            email.name = google_user["name"]
            db.add(create_user)
            db.commit()
            db.refresh(create_user)
            return email
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
        db.add(user_auth)
        db.commit()
        db.refresh(user_auth)
        return user
    
def create_l_user(email_id:str,password:str,db:Session):
    hash_pass = hash_password(password)

    email = db.query(User).filter(User.email==email_id).first()

    if email:
        check = db.query(UserAuth).filter(UserAuth.user_id==email.id,UserAuth.provider=="local").first()# further here too add passowrd login feature
        if check:
            raise HTTPException(status_code=403,detail="This email is already in use")
        user_auth = UserAuth(
            provider="local",
            user_id = email.id,
            hashed_password=hash_pass
        )
        try:
            db.add(user_auth)
            db.commit()
        except:
            db.rollback()
            raise
        return email
    
    create = User(
        email = email_id
    )
    db.add(create)
    db.flush()
    auth = UserAuth(
        provider = "local",
        user_id = create.id,
        hashed_password=hash_pass
    )
    try:
        db.add(auth)
        db.commit()
        db.refresh(auth)
    except:
        db.rollback()
        raise

    return create

def login_l_user(email_id:str,password:str,db:Session):
    email = db.query(User).filter(User.email==email_id).first()
    if not email:
        raise HTTPException(status_code=400,detail="Wrong credentials")
    
    check = db.query(UserAuth).filter(UserAuth.user_id==email.id,UserAuth.provider=="local").first()

    if not check:
        raise HTTPException(status_code=400,detail="Add password to this email through create user")
    
    if not verify_password(password,check.hashed_password):
        raise HTTPException(status_code=400,detail="Wrong credentials")
    
    return email


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





    

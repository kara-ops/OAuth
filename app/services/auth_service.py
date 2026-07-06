from sqlalchemy.orm import Session
from app.models.user_model import User,UserAuth
from fastapi import Request,HTTPException
from app.utils.hashing import hash_password,verify_password
from app.utils.code_gen import gen_code
from app.services.token_service import forgot_pass_key,get_forgot_pass_key
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
        db.add(user_auth)
        db.commit()
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
    db.add(auth)
    db.commit()
    db.refresh(auth)
    return create

def login_l_user(email_id:str,password:str,db:Session):
    email = db.query(User).filter(User.email==email_id).first()
    if not email:
        raise HTTPException(status_code=400,detail="User does not exist")
    
    check = db.query(UserAuth).filter(UserAuth.user_id==email.id,UserAuth.provider=="local").first()

    if not check:
        raise HTTPException(status_code=400,detail="Add password to this email through create user")
    
    if not verify_password(password,check.hashed_password):
        raise HTTPException(status_code=400,detail="Wrong password")
    
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
    auth_check.hashed_password=new_pass
    db.commit()
    return {"successfully changed"}

def forgot_password(email:str,db:Session):
    check = db.query(User).filter(User.email==email).first()
    if not check:
        return {"You will recieve a email with a code"}
    
    code = gen_code()
    set_code = forgot_pass_key(check.id,code)
    mail = forgot_pass_mail(code,"gay")
    return {"You will recieve a email with a code"}



    



    

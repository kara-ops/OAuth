from sqlalchemy.orm import Session
from app.models.user_model import User,UserAuth
from fastapi import Request,HTTPException
from app.utils.hashing import hash_password,verify_password


def get_or_create_user(db:Session, google_user:dict)->User:
    email = db.query(User).filter(User.email==google_user["email"]).first()
    if email:
        check = db.query(UserAuth).filter(UserAuth.user_id==email.user_id).first()
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
    
def create_l_user(email:str,password:str,db:Session):
    email = db.query(User).filter(User.email==email).first()
    if email:
        raise HTTPException(status_code=400,detail="Email already in use")
    h_pass = hash_password(password)
    create = User(
        email = email
    )
    db.add(create)
    db.flush()
    auth = UserAuth(
        provider = "local",
        user_id = create.id
    )
    db.add(auth)
    db.commit()
    db.refresh(auth)

def login_l_user(email:str,password:str,db:Session):
    email = db.query(User).filter(User.email==email).first()
    if not email:
        raise HTTPException(status_code=400,detail="User does not exist")
    if not verify_password(password,email.auth.hashed_password):
        raise HTTPException(status_code=400,detail="Wrong password")
    return email






    

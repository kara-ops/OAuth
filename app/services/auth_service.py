from sqlalchemy.orm import Session
from app.models.user_model import User,UserAuth
from fastapi import Request


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
    

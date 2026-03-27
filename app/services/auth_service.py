from sqlalchemy.orm import Session
from app.models.user_model import User


def get_or_create_user(db:Session, google_user:dict)->User:
    get_user = db.query(User).filter(User.google_id==google_user["id"]).first()
    if not get_user:
        create_user = User(
            email = google_user["email"],
            google_id = google_user["id"],
            name = google_user["name"]
        )
        db.add(create_user)
        db.commit()
        db.refresh(create_user)
        return create_user
    else:
        return get_user

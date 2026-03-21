from sqlalchemy import Column, String, Integer, DateTime
from app.database.postgres import Base
from datetime import datetime, timezone



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True)
    email = Column(String, nullable = False, unique = True)
    name = Column(String, nullable = True)
    google_id = Column(String, unique = True, nullable = False)
    created_at = Column(DateTime,default = lambda: datetime.now(timezone.utc) )


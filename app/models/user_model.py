from sqlalchemy import Column, String, Integer, DateTime, Boolean, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.postgres import Base
from datetime import datetime, timezone



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key = True)
    email = Column(String, nullable = False, unique = True)
    name = Column(String, nullable = True)
    is_active = Column(Boolean,default=True,nullable=False)
    created_at = Column(DateTime,server_default=func.now(),nullable=False)
    avatar_url = Column(String,nullable=True)

    auth = relationship("UserAuth",back_populates="user",cascade="all, delete")

class UserAuth(Base):
    __tablename__ = "user_auth"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    hashed_password = Column(String,nullable=True)
    provider = Column(String,nullable=False,)#[local,google,etc]
    provider_id = Column(String, nullable=True)
    created_at = Column(DateTime,server_default=func.now(),nullable=False)

    __table_args__ = (
        UniqueConstraint("provider","provider_id", name="uq_provider_provider_id"),
    )

    user = relationship("User",back_populates="auth")


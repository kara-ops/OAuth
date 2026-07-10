from sqlalchemy import Column, String, Integer, DateTime, Boolean, func, ForeignKey, UniqueConstraint, UUID
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
    session = relationship("Session",back_populates="user",cascade="all, delete")

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


class UserSession(Base):
    __tablename__ = "user_session"
    id = Column(Integer,primary_key=True,nullable=False)
    session_id = Column(UUID,unique=True,nullable=False)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False,index=True)

    r_token_hash = Column(String(64),nullable=False)
    revoked_at = Column(DateTime,nullable=True)

    device_type = Column(String)
    device_name = Column(String)
    browser = Column(String)
    os = Column(String)

    ip_address = Column(String,nullable=False)
    user_agent = Column(String)

    created_at = Column(DateTime,server_default=func.now(),nullable=False)
    expires_at = Column(DateTime,nullable=False,index=True)
    last_seen = Column(DateTime,server_default=func.now(),nullable=False)

    user = relationship("User",back_populates="session")
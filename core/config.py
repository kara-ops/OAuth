from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GOOGLE_CLIENT_ID : str 
    GOOGLE_SECRET : str 
    GOOGLE_REDIRECT_URL : str

    SECRET_KEY : str 
    REFRESh_TOKEN_EXPIRE_DAYS : int = 7
    ALGORITHM : str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 15

    DATABASE_URL : str 

    REDIS_URL : str 

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()





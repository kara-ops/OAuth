from fastapi import FastAPI
from sqlalchemy import text
from contextlib import asynccontextmanager
from app.database.postgres import Sessionlocal
from app.database.redis import get_redis
from app.router import auth_routers



@asynccontextmanager
async def lifespan(app:FastAPI):
    try :
        db = Sessionlocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("db working")
    except Exception as e:
        raise RuntimeError(f"Postgress Connection failed {e}")
    
    try :
        redis = get_redis()
        pong = redis.ping()
        print("Redis connection working")
    except Exception as e:
        raise RuntimeError(F"Redis connection failed {e}")
    
    yield

    app.include_router(auth_routers)

    print("App shuting down")
    


app = FastAPI(lifespan=lifespan)

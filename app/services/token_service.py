from app.database.redis import get_redis
import json

def store_refresh_token(user_id:int, refresh_token:str)->None:
    redis = get_redis()
    key = f"refresh:{user_id}"
    ttl = 60*60*24*7
    redis.setex(key, ttl, refresh_token)
    
def verify_refresh_token(user_id:int, refresh_token:str)->bool:
    key = f"refresh:{user_id}"
    redis = get_redis()
    check_value = redis.get(key)
    return check_value==refresh_token

def delete_refresh_token(user_id:int)->None:
    redis = get_redis()
    key = f"refresh:{user_id}"
    redis.delete(key)

def blacklist_token(jti:str, ttl:int)->None:
    redis = get_redis()
    key = f"blacklist:{jti}"
    redis.setex(key, ttl, "1")

def is_blacklisted(jti:str)->bool:
    redis = get_redis()
    key = f"blacklist:{jti}"
    return redis.exists(key)==1

def rate_limiter(ip:str)->bool:
    redis = get_redis()
    ttl = 60
    key = f"login attempts:{ip}"
    attemps = redis.incr(key)
    if attemps == 1:
        redis.expire(key, ttl)

    if attemps >= 5:
        return False
    else:
        return True
    
def forgot_pass_key(token:str,user_id:int,code:str):
    redis = get_redis()
    ttl = 60*8
    key = f"reset:{token}:{code}"
    redis.setex(key,ttl,user_id)

def get_forgot_pass_key(token:str,code:str):
    redis = get_redis()
    key = f"reset:{token}:{code}"
    return redis.get(key)

def del_forgot_pass_key(token:str,code:str):
    redis = get_redis()
    key = f"reset:{token}:{code}"
    redis.delete(key)

def concurrent_first_request(sid):
    redis = get_redis()
    key = f"concurrent_refresh:{sid}"
    value = {"status":"refreshing"}
    return redis.set(key,json.dumps(value),10,nx=True)

def concurrent_r_token(sid,a_token:str,r_token:str):
    redis = get_redis()
    key = f"concurrent_refresh:{sid}"
    value = {"status":"done",
             "access":a_token,
             "refresh":r_token}
    redis.set(key,json.dumps(value),10)


def get_concurrent_r_token(sid):
    redis = get_redis()
    key = f"concurrent_refresh:{sid}"
    data = redis.get(key)
    if data:
        return json.loads(data)
    else:
        return None





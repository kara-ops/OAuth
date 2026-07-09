import string
import secrets, uuid

def gen_code():
    alphabet = string.ascii_uppercase + string.digits
    code = ''.join(secrets.choice(alphabet) for _ in range(6))
    return code
def gen_url_token():
    return secrets.token_urlsafe(32)

def get_uuid():
    return uuid.uuid4()

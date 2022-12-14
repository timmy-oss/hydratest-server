from .db import redis_db
from .utils import jwt_decode
from models.settings import Settings
from jsonrpcserver import JsonRpcError

settings = Settings()

def  get_user_from_token( token  ):

    err, payload = jwt_decode( token, settings.jwt_secret)

    if err:
        raise JsonRpcError(401, "invalid jwt")


    matching_users = redis_db.json().get("users", f"$[?@.id == '{payload['sub']}' ]")
    
    if len(matching_users) == 0:
        raise JsonRpcError(401, 'invalid jwt')


    return matching_users[0]
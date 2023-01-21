from pydantic import ValidationError
from nanoid import generate
from jose import jwt
from jose.exceptions import ExpiredSignatureError
from models.users import AuthTokenModel
from jsonrpcserver import JsonRpcError
from models.settings import Settings
from .db import redis_db
from uuid import uuid4
from models.settings import RequestModel
import scrypt



settings = Settings()



def gen_uid():
    return generate("1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", 8)
    

def generate_user_id():
    return generate("1234567890", 6)


def hash_password( password , salt):
    return scrypt.hash(password, salt).hex()


def verify_password( hash, guessed, salt ):
    return scrypt.hash(guessed, salt).hex() == hash



def jwt_encode( payload, secret ):
    return jwt.encode( payload, secret, algorithm= 'HS256')


def jwt_decode( token, secret):
    try:
        payload= jwt.decode( token, secret, algorithms= ['HS256'] ) 

        return None, payload


    except ExpiredSignatureError:
        return { "msg" : "Session expired" }, None


    except Exception as e:
        return {"msg" : str(e) }, None




def model_validate(cls, data):
    if not isinstance(data, dict):
        return { "msg" : f'expected dict, got {type(data)}' }, None
    try:
        model = cls(**data)
        return None, model

    except ValidationError as error:
        return error.json(), None





def validate_req(req):
    e,m = model_validate(RequestModel, req)

    if e:
        raise JsonRpcError(-32602, "invalid params", e)

    return m




def authenticate_user( tokenObj ):

    err, model = model_validate(AuthTokenModel, tokenObj)

    if err:
        raise JsonRpcError(-32602, "invalid token object", err) 

    data = model.dict()


    error, payload  = jwt_decode(data['token'], settings.jwt_secret)

    if error:
        raise JsonRpcError(401, error["msg"], error)

    id = payload['sub']


    users_matching = redis_db.json().get("users", f"$[?@.id == '{id}'] ")

    if len(users_matching) == 0:
        raise JsonRpcError(401, "invalid credentials")

    user = users_matching[0]

    return (user,payload)



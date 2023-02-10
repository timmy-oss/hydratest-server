from jsonrpcserver import method, JsonRpcError, InvalidParams, Success
from lib.db import redis_db
from lib.utils import model_validate, authenticate_user, validate_req
from models.settings import Settings

settings = Settings()



@method( name = "sessions.all")
async def list_all_sessions(req):
    req = validate_req(req)

    user, payload =  authenticate_user(req.auth)
    user_id = user['id']

    sessions = user["sessions"]

    return Success({
        "ok" : True,
        "data" : sessions
    })


@method( name = "sessions.active")
async def list_active_sessions(req):
    req = validate_req(req)

    user, payload =  authenticate_user(req.auth)
    user_id = user['id']

    sessions = user["sessions"]

    return Success({
        "ok" : True,
        "data" : sessions
    })


@method( name = "sessions.inactive")
async def list_inactive_sessions(req):
    req = validate_req(req)

    user, payload =  authenticate_user(req.auth)
    user_id = user['id']

    sessions = user["sessions"]

    return Success({
        "ok" : True,
        "data" : sessions
    })



@method( name = "sessions.submitted")
async def list_submitted_sessions(req):
    req = validate_req(req)

    user, payload =  authenticate_user(req.auth)
    user_id = user['id']

    sessions = user["sessions"]

    return Success({
        "ok" : True,
        "data" : sessions
    })


@method(name = "sessions.get_one")
async def get_session(req):

    req = validate_req(req)

    user, payload =  authenticate_user(req.auth)

    sessions_keys = user['sessions']



    session = redis_db.json().get( req.body['sessionId'] )


    return Success({
        "ok" : True,
        "data" : session
    })

   



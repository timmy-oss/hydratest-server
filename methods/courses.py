from jsonrpcserver import method, JsonRpcError, Error, InvalidParams, Success
from models.courses import CreateCourseInputModel
from lib.utils import model_validate, authenticate_user, validate_req
from lib.db import redis_db
from models.settings import Settings



settings = Settings()


@method( name = "courses.create")
async def add_new_course(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)
    
    err,model = model_validate(CreateCourseInputModel, req.body)

    if err:
        return InvalidParams(err)

    data = model.dict()

    matching = redis_db.json().get("courses", f"$[?@.course_title == '{model.course_title}' ]")

    if len(matching) > 0:
        raise JsonRpcError(403, "course with title exists already")

    redis_db.json().arrappend("courses", "$", data)

    return Success({
        "ok" : True,
        "data" : model.dict(by_alias = True)
    })




@method( name = "courses.list")
async def list_all_course(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)
    

    matching = redis_db.json().get("courses", f"$")


    return Success({
        "ok" : True,
        "data" : matching[0]
    })

    





from jsonrpcserver import method, JsonRpcError, Error, InvalidParams, Success
from models.exams import CreateExamInputModel
from lib.utils import model_validate, authenticate_user, validate_req
from lib.db import redis_db
from models.settings import Settings



settings = Settings()


@method( name = "exams.create")
async def add_new_exam(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)
    
    err,model = model_validate(CreateExamInputModel, req.body)

    if err:
        return InvalidParams(err)

    data = model.dict()

    matching_courses = redis_db.json().get("courses", f"$[?@.id == '{model.course_id}' ]")

    if len(matching_courses) == 0:
        raise JsonRpcError(403, "Course specified does not exist")


    matching = redis_db.json().get("exams", f"$[?@.exam_title == '{model.exam_title}' ]")

    if len(matching) > 0:
        raise JsonRpcError(403, "exam with title exists already")


    data.update({
        "course" : matching_courses[0]
    })

    redis_db.json().arrappend("exams", "$", data)

    return Success({
        "ok" : True,
        "data" : model.dict(by_alias = True)
    })




@method( name = "exams.list")
async def list_all_exam(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)
    

    matching = redis_db.json().get("exams", f"$")


    return Success({
        "ok" : True,
        "data" : matching[0]
    })




@method( name = "exams.get_one")
async def get_one_exam(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)
    
    id = req.body['id']

    matching = redis_db.json().get("exams", f"$[?@.id == '{id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "exam with id does not exists")


    return Success({
        "ok" : True,
        "data" : matching[0]
    })

    





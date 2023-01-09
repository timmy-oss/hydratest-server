from jsonrpcserver import method, JsonRpcError, Error, InvalidParams, Success
from models.courses import CreateCourseInputModel, CourseQuestion
from lib.utils import model_validate, authenticate_user, validate_req
from lib.db import redis_db
from models.settings import Settings
from time import time


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




@method( name = "courses.get_one")
async def get_one_course(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)
    
    id = req.body['id']

    matching = redis_db.json().get("courses", f"$[?@.id == '{id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "course with id does not exists")


    return Success({
        "ok" : True,
        "data" : matching[0]
    })


@method( name = "courses.add_question")
async def add_course_question(req):
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    err,model = model_validate(CourseQuestion, req.body)

    if err:
        return InvalidParams(err)

    course_question = model.dict()

    course_question.update({
        "author" : user['id'],
        "created" : time(),
        "last_updated" : time()
    })

    redis_db.json().arrappend("course_questions", "$", course_question)

    return Success({
        "ok" : True,
        "data" : course_question
    })



# Get All questions under a course


@method( name = "courses.get_questions")
async def get_course_questions(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)
    
    id = req.body['courseId']

    matching = redis_db.json().get("course_questions", f"$[?@.course == '{id}' ]")


    return Success({
        "ok" : True,
        "data" : matching
    })



 





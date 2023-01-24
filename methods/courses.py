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
    })

    redis_db.json().arrappend("course_questions", "$", course_question)

    return Success({
        "ok" : True,
        "data" : course_question
    })





@method( name = "courses.edit_question")
async def edit_course_question(req):
    req = validate_req(req)

    authenticate_user(req.auth)

    id = req.body['questionId']

    matching = redis_db.json().get("course_questions", f"$[?@.id == '{id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "Question with id does not exists")

    q = matching[0]

    course_question_dict = q;
    course_question_dict.update(req.body)

    print(req.body)

    course_question_model = CourseQuestion(**course_question_dict)
    new_course_question = course_question_model.dict()
    new_course_question.update({"last_updated" : time()})

    redis_db.json().set("course_questions", f"$[?@.id == '{id}']", new_course_question)

    return Success({
        "ok" : True,
        "data" : new_course_question
    })



# Get All questions under a course


@method( name = "courses.get_course_questions")
async def get_course_questions(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)
    
    id = req.body['courseId']

    matching = redis_db.json().get("course_questions", f"$[?@.course == '{id}' ]")[:20]


    # print(matching)


    return Success({
        "ok" : True,
        "data" : matching
    })




@method( name = "courses.questions.get_meta")
async def get_question_meta(req):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    response_data = {}
    
    id = req.body['id']

    matching = redis_db.json().get("course_questions", f"$[?@.id == '{id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "Question with id does not exists")

    q = matching[0]
    q_upvotes = q.get('upvotes',[])
    q_downvotes = q.get('downvotes',[])
    q_flags = q.get('flags',[])

    response_data.update({
        "upvote" : {
            "upvotes" : len(q_upvotes),
            "upvoted" : user['id'] in q_upvotes
        },
         "downvote" : {
            "downvotes" : len(q_downvotes),
            "downvoted" : user['id'] in q_downvotes
        },
         "flag" : {
            "flags" : len(q_flags),
            "flagged" : user['id'] in q_flags
        },
    })

    return Success({
        "ok" : True,
        "data" : response_data
    })


@method( name = "courses.questions.upvote")
async def upvote_question(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)


    response_data = {}
    
    id = req.body['id']

    matching = redis_db.json().get("course_questions", f"$[?@.id == '{id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "Question with id does not exists")

    q = matching[0]
    q_upvotes = q.get('upvotes',[])
    print(q_upvotes,q)

    if not user['id'] in q_upvotes:
        redis_db.json().arrappend("course_questions", f"$[?@.id == '{id}'].upvotes", user['id'] )
        response_data.update({
            'upvoted' : True,
            'upvotes' : len(q_upvotes) + 1
        })
    else:
        filtered_upvotes =  filter(lambda x : not x == user['id'] , q_upvotes)
        
        redis_db.json().set("course_questions", f"$[?@.id == '{id}'].upvotes", list(filtered_upvotes) )

        response_data.update({
            'upvoted' : False,
            'upvotes' : len(q_upvotes) - 1

        })


    return Success({
        "ok" : True,
        "data" : response_data
    })



@method( name = "courses.questions.downvote")
async def downvote_question(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)


    response_data = {}
    
    id = req.body['id']

    matching = redis_db.json().get("course_questions", f"$[?@.id == '{id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "Question with id does not exists")

    q = matching[0]
    q_downvotes = q.get('downvotes',[])


    if not user['id'] in q_downvotes:
        redis_db.json().arrappend("course_questions", f"$[?@.id == '{id}'].downvotes", user['id'] )
        response_data.update({
            'downvoted' : True,
            'downvotes' : len(q_downvotes) + 1
        })
    else:
        filtered_downvotes =  filter(lambda x : not x == user['id'] , q_downvotes)
        
        redis_db.json().set("course_questions", f"$[?@.id == '{id}'].downvotes", list(filtered_downvotes) )

        response_data.update({
            'downvoted' : False,
            'downvotes' : len(q_downvotes) - 1

        })


    return Success({
        "ok" : True,
        "data" : response_data
    })




@method( name = "courses.questions.flag")
async def flag_question(  req  ):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)


    response_data = {}
    
    id = req.body['id']

    matching = redis_db.json().get("course_questions", f"$[?@.id == '{id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "Question with id does not exists")

    q = matching[0]
    q_flags = q.get('flags',[])


    if not user['id'] in q_flags:
        redis_db.json().arrappend("course_questions", f"$[?@.id == '{id}'].flags", user['id'] )
        response_data.update({
            'flagged' : True,
            'flags' : len(q_flags) + 1
        })
    else:
        filtered_flags =  filter(lambda x : not x == user['id'] , q_flags)
        
        redis_db.json().set("course_questions", f"$[?@.id == '{id}'].flags", list(filtered_flags) )

        response_data.update({
            'flagged' : False,
            'flags' : len(q_flags) - 1

        })


    return Success({
        "ok" : True,
        "data" : response_data
    })




 





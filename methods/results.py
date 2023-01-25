from jsonrpcserver import method, JsonRpcError, InvalidParams, Success
from lib.db import redis_db
from lib.utils import model_validate, authenticate_user, validate_req
from models.settings import Settings
from models.exams import GenerateResultInput, Remark, Result

settings = Settings()


def filter_func(d):

    return not d.get('result_generated', False)


def map_func(k):
    d = redis_db.json().get(f"{k}", "$")
    if d and len(d) >0:
        d[0].update({ "key"  : k })
        return d[0]

    return None


@method( name = "results.list")
async def list_results(req):
    req = validate_req(req)

    user, payload =  authenticate_user(req.auth)
    user_id = user['id']

    results = redis_db.json().get("results", f"$[?@.user =='{user_id}' ]" )

    return Success({
        "ok" : True,
        "data" : results
    })






@method(name = "results.get_pending_results")
async def get_pending_results(req):
    req = validate_req(req)

    user, payload =  authenticate_user(req.auth)

    sessions_keys = user['sessions']    

    sessions = list(filter( lambda x : x is not None, list(map( map_func, sessions_keys )) ))
    # print(sessions)
    pending_sessions = list(filter( filter_func, sessions))

    # print(pending_sessions)
    return Success({
        "ok" : True,
        "data"  : pending_sessions
    })





@method( name = "results.generate")
async def generate_result_from_session(req):
    req = validate_req(req)

    user,payload = authenticate_user(req.auth)

    err, model = model_validate(GenerateResultInput, req.body)

    if err:
        return InvalidParams(err)

    sessions = redis_db.json().get(f"{model.session_key}", "$" )

    if not sessions or len(sessions) == 0:
        raise JsonRpcError(404, "Session with key does not exist", {"message" : "Session with key does not exist"})

    session = sessions[0]

    if  session['is_active'] or not session['submitted']:
        raise JsonRpcError(404, "Session is still active", {"message" : "Session is still active"})
    
    session_id = session['id']
    responses = redis_db.json().get("examresponses", f"$[?@.session == '{session_id}' ]")

    correct_responses = list(filter( lambda x: x['is_correct'], responses ))

    incorrect_responses = list(filter( lambda x: not x['is_correct'], responses ))

    correct_responses_question_ids = list(map(lambda x: x['question'], correct_responses))

    incorrect_responses_question_ids = list(map(lambda x: x['question'], incorrect_responses))

    remark = None
    correct_attempts = len(correct_responses)
    incorrect_attempts = len(incorrect_responses)
    attempts = len(responses)
    total_attempts = len(session['question_ids'])
    score = round((correct_attempts / total_attempts) * 100, 2)

    if score >= 0 and score <= 50:
        remark = Remark._failed
    elif score > 50 and score <= 60:
        remark = Remark._passed
    elif score > 60 and score <= 70:
        remark = Remark._credit
    elif score > 70 and score <= 100:
        remark = Remark._dinstinction
    else:
        remark = Remark._unknown

    exam_id = session['exam']
    matching = redis_db.json().get("exams", f"$[?@.id == '{exam_id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "exam with id does not exists")
    
    exam = matching[0]


    result_map = []

    for qid in session['question_ids']:
        if qid in correct_responses_question_ids:
            result_map.append("T")
        elif qid in incorrect_responses_question_ids:
            result_map.append("F")
        else:
            result_map.append("N")


    # print(result_map)


    result  =  Result(
        correct_attempts = correct_attempts,
        incorrect_attempts = incorrect_attempts,
        total_attempts = total_attempts,
        attempts=attempts,
        score  = score,
        remark= remark,
        session_key= model.session_key,
        exam = session['exam'],
        exam_name = exam['exam_title'],
        course_name = exam['course']['course_title'],
        course = exam['course']['id'],
        user = user['id'],
        allow_pdf = model.generate_pdf,
        map_info = result_map
    )

    # print(result.dict())

    redis_db.json().arrappend("results", "$", result.dict() )

    redis_db.json().set(f"{model.session_key}", "$.result_generated", True )

    return Success({
        "ok" : True,
        "data" : result.dict(by_alias = True)
    })

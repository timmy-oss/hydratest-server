from jsonrpcserver import method, JsonRpcError, InvalidParams, Success
from lib.db import redis_db
from lib.utils import model_validate, authenticate_user, validate_req
from models.exams import CreateExamInputModel, CreateExamSessionInput,  ExamSession, ExamSessionResponse
from models.settings import Settings
from time import time
import rsa,random

settings = Settings()


@method(name="exams.create")
async def add_new_exam(req):
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    err, model = model_validate(CreateExamInputModel, req.body)

    if err:
        return InvalidParams(err)

    data = model.dict()

    matching_courses = redis_db.json().get(
        "courses", f"$[?@.id == '{model.course_id}' ]")

    if len(matching_courses) == 0:
        raise JsonRpcError(403, "Course specified does not exist")

    matching = redis_db.json().get(
        "exams", f"$[?@.exam_title == '{model.exam_title}' ]")

    if len(matching) > 0:
        raise JsonRpcError(403, "exam with title exists already")

    data.update({
        "course": matching_courses[0]
    })

    redis_db.json().arrappend("exams", "$", data)

    return Success({
        "ok": True,
        "data": model.dict(by_alias=True)
    })


@method(name="exams.list")
async def list_all_exam(req):
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    matching = redis_db.json().get("exams", f"$")

    return Success({
        "ok": True,
        "data": matching[0]
    })


@method(name="exams.get_one")
async def get_one_exam(req):
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    id = req.body['id']

    matching = redis_db.json().get("exams", f"$[?@.id == '{id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "exam with id does not exists")

    return Success({
        "ok": True,
        "data": matching[0]
    })


@method(name = "exams.session.heartbeat")
async def session_heartbeat(req):
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    exam_id = req.body['exam']
    matching = redis_db.json().get("exams", f"$[?@.id == '{exam_id}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "exam with id does not exist")

    exam = matching[0]

    sessions = redis_db.json().get(f"examsession:{user['id']}:{exam_id}", "$" )

    if sessions and len(sessions) == 0:
        raise InvalidParams("user has no active session")

    session = sessions[0]

    if not session['id'] == req.body['id']:
        raise JsonRpcError(403, "Session ID conflict detected", { "message" : "Session ID conflict detected"}) 

    elapsed_time = session['elapsed_time']
    diff_in_time = None

    if req.body['init'] == False and ( elapsed_time < exam['time_allowed'] * 60 ):
        if session['last_ping']:
            diff_in_time = time() -  session['last_ping']
        else:
            diff_in_time = float(session['ping_interval'])
        redis_db.json().set(f"examsession:{user['id']}:{exam_id}", "$.elapsed_time", float(elapsed_time) + float(diff_in_time)  )
        redis_db.json().set(f"examsession:{user['id']}:{exam_id}", "$.last_ping", time() )

    refreshed_session = redis_db.json().get(f"examsession:{user['id']}:{exam_id}", "$" )[0]


    session_model = ExamSession(**refreshed_session)

    return Success({
        "ok": True,
        "data": {
        "session" :session_model.dict(exclude={'private_key', 'peer_public_key'}),
        "auto_submit" : session_model.elapsed_time >= (exam['time_allowed'] * 60)
        }
    })



@method(name="exams.create_session")
async def create_exam_session(req):
    
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    err, model = model_validate(CreateExamSessionInput, req.body)
    
    if err:
        return InvalidParams(err)
        
    matching = redis_db.json().get("exams", f"$[?@.id == '{model.exam}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "exam with id does not exist")

    exam = matching[0]


    sessions = redis_db.json().get(f"examsession:{user['id']}:{exam['id']}", "$" )


    allowed_intents = ["resume", "new"]

    intent = req.body['intent']

    if not intent in allowed_intents:
        intent = "resume"

    if sessions  and len(sessions) > 0 and intent == "resume":
        session = sessions[0]

        session_model = ExamSession(**session)

        if session_model.is_active and not session_model.submitted:
        
            return Success({
        "ok": True,
        "data": session_model.dict(exclude={'private_key', 'peer_public_key'})
    })
        
        else:
            raise JsonRpcError(403, "Inactive Sesssion", { "message" : "Inactive Session"})
        


    elif intent == "new":



        priv_key = pub_key = peer_public_key  = None


        try:
            
            peer_public_key = rsa.PublicKey.load_pkcs1(model.key.encode())

            pub_key, priv_key = rsa.newkeys(512)

        except Exception as e:
            raise JsonRpcError(403, str(e), {"message" : str(e)})


    
        all_qids = redis_db.json().get("course_questions",f"$[?@.course == '{exam['course']['id']}'].id" )

        number_of_questions_in_course = len(all_qids)

        # print("Questions: ", number_of_questions_in_course)

        if number_of_questions_in_course < exam['number_of_questions']:
            raise JsonRpcError(403, "Not enough questions for selected course", {"message" : "Not enough questions for selected course"})


        qids = []


        start = 0
        while start < min( exam['number_of_questions'], number_of_questions_in_course):
            x = random.randint(0, min( exam['number_of_questions'], number_of_questions_in_course) -1)
            if all_qids[x] in qids:
                continue
            start += 1
            qids.append(all_qids[x])


        session = ExamSession(
            peer_public_key = peer_public_key.save_pkcs1().decode(),
            private_key = priv_key.save_pkcs1().decode(),
            public_key = pub_key.save_pkcs1().decode(),
            exam = model.exam,
            user = user['id'],
            ping_interval = settings.ping_interval,
            question_ids = qids,
            name = f"{exam['exam_title']} - {exam['course']['course_title']} - {time()} "
        )

        session_dict = session.dict()

        redis_db.json().set(f"examsession:{user['id']}:{model.exam}", "$", session_dict )

        session_key = f"examsession:{user['id']}:{model.exam}"
        user_id = user['id']
        redis_db.json().arrappend("users", f"$[?@.id == '{user_id}'].sessions", session_key )


        return Success({
            "ok": True,
            "data": session.dict(exclude={'private_key', 'peer_public_key'})
        })

    else:
        raise JsonRpcError(403, "Invalid intent.", {"messsage" : "Invalid intent."})




@method(name="exams.session.get_question")
async def get_exam_session_question(req):
    
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    exam_id = req.body['exam']

    sessions = redis_db.json().get(f"examsession:{user['id']}:{exam_id}", "$" )

    if sessions and len(sessions) == 0:
        raise InvalidParams("user has no active session")

    # print(sessions)
    session = sessions[0]
    # print(session['id'], req.body['id'])

    if not session['id'] == req.body['sessionId']:
        raise JsonRpcError(403, "Session ID conflict detected", { "message" : "Session ID conflict detected"}) 


    qid = req.body['id']
    # print(qid, session['question_ids'])
    if not qid in session['question_ids']:
        raise JsonRpcError(403, "Question not tied to session", { "message" : "Question not tied to session"}) 

    matching = redis_db.json().get("course_questions", f"$[?@.id == '{qid}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "Question with id does not exists")

    q = matching[0]
    q.update({
        "correct_option" : None,
        "answer" : None
    })

    session_model = ExamSession(**session)

    q_response = None


    if q['id'] in session_model.attempted_question_ids:

        q_id  =q['id']
        s_id = session['id']


        question_responses = redis_db.json().get("examresponses", f"$[?@.question == '{q_id}' && @.session == '{s_id}' ]"  )
        
        if len(question_responses) > 0:
            q_response = ExamSessionResponse(**question_responses[0])


    q_response_data = None

    if q_response:
        q_response_data = q_response.dict(exclude = {'is_correct',})  

    return Success({
        "ok": True,
        "data": {
        "session" :  session_model.dict(exclude={'private_key', 'peer_public_key'}),
        "question" : q,
        "response" :  q_response_data
        
        }
    })


@method(name = "exams.session.submit")
async def submit_exam(req):

    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    exam_id = req.body['exam']
    sessions = redis_db.json().get(f"examsession:{user['id']}:{exam_id}", "$" )

    if sessions and len(sessions) == 0:
        raise InvalidParams("user has no active session.")

    session = sessions[0]
    
    if (not session['id'] == req.body['sessionId']) and not req.body.get("lax",False):
        raise JsonRpcError(403, "Session ID conflict detected", { "message" : "Session ID conflict detected"}) 
    

    if not session['is_active'] or session['submitted']:
        raise JsonRpcError(403, "Session is inactive.", {"message" : "Session is inactive."})

    
    sid = f"examsession:{user['id']}:{exam_id}"

    if req.body.get("lax",False):
        sid = req.body["sessionId"]

    
    redis_db.json().set(sid, "$.submitted", True  )
    redis_db.json().set(sid, "$.is_active", False  )

    return Success({
        "ok": True,
        "data":{
        "submitted" : True
        }

    })

    



@method(name="exams.session.submit_response")
async def submit_question_response(req):
    
    req = validate_req(req)

    user, payload = authenticate_user(req.auth)

    exam_id = req.body['exam']
    sessions = redis_db.json().get(f"examsession:{user['id']}:{exam_id}", "$" )

    if sessions and len(sessions) == 0:
        raise InvalidParams("user has no active session")

    # print(sessions)
    session = sessions[0]
    # print(session['id'], req.body['id'])

    if not session['id'] == req.body['sessionId']:
        raise JsonRpcError(403, "Session ID conflict detected", { "message" : "Session ID conflict detected"}) 
    
    # private_key = peer_public_key = response = None

    # try:
 
    #     private_key = rsa.PrivateKey.load_pkcs1(session['private_key'].encode(), "PEM")
    #     peer_public_key  = rsa.PublicKey.load_pkcs1(session['peer_public_key'].encode(), "PEM")

    #     response = rsa.decrypt( bytes.fromhex(req.body['response']) , private_key)

    # except Exception as e:
    #     print(e)
    #     raise JsonRpcError(403, str(e), {"message" : str(e)})

    
    decoded_response = req.body['response']
    qid = decoded_response['qid']

    # # print(qid, session['question_ids'])
    if not qid in session['question_ids']:
        raise JsonRpcError(403, "Question not tied to session", { "message" : "Question not tied to session"}) 

    matching = redis_db.json().get("course_questions", f"$[?@.id == '{qid}' ]")

    if len(matching) == 0:
        raise JsonRpcError(403, "Question with id does not exists")

    q = matching[0]

    test_match = lambda x,y : not x.strip().upper().find(y.strip().upper()) == -1

    is_correct_answer = False

    if q['question_type'] == 'objective' and decoded_response['answer'].strip().upper() == q['correct_option'].strip().upper():
        is_correct_answer = True


    if q['question_type'] == 'germane' and test_match(q['answer'], decoded_response['answer']):
        is_correct_answer = True


    session_model = ExamSession(**session);

    if not qid in session_model.attempted_question_ids:
        redis_db.json().arrappend(f"examsession:{user['id']}:{exam_id}", "$.attempted_question_ids" , qid )
        session_model.attempted_question_ids.append( qid );

    q_id = q['id']
    s_id = session['id']  

    question_responses = redis_db.json().get("examresponses", f"$[?@.question == '{q_id}' && @.session == '{s_id}' ]"  )
    
    if len(question_responses) > 0:
        q_response = ExamSessionResponse(**question_responses[0])
        q_response.response = decoded_response['answer']
        q_response.response_content = decoded_response['answer'] if q['question_type'] == "germane" else q[f"option_{decoded_response['answer'].strip().upper()}"]
        q_response.is_correct = is_correct_answer
        q_response.edits += 1

        redis_db.json().set("examresponses", f"$[?@.question == '{q_id}' && @.session == '{s_id}' ]" , q_response.dict() )


        return Success({
        "ok": True,
        "data": {
        "exam_session_response" : q_response.dict() ,
        "session" : session_model.dict(exclude = { "private_key", "peer_public_key"})
        }
    })

    else:

        exam_session_response_model = ExamSessionResponse(
            session = session['id'],
            question = qid,
            response = decoded_response['answer'],
            response_content = decoded_response['answer'] if q['question_type'] == "germane" else q[f"option_{decoded_response['answer'].strip().upper()}"],
            is_correct = is_correct_answer
        )

        exam_session_response = exam_session_response_model.dict()

        redis_db.json().arrappend("examresponses","$", exam_session_response  )

        return Success({
            "ok": True,
            "data": {
            "exam_session_response" : exam_session_response ,
            "session" : session_model.dict(exclude = { "private_key", "peer_public_key"})
            }
        })


    

from pydantic import BaseModel, Field, HttpUrl, validator
from lib.utils import gen_uid
from typing import Union
from time import time

class CreateExamInputModel(BaseModel):
    id : str = Field( default_factory= gen_uid)
    exam_title : str = Field(min_length = 8, alias = "examTitle", )
    instant_result : bool = Field(alias = "instantResult")
    course_id : str  = Field(alias = "courseId", default= None)
    time_allowed : int = Field(alias = "timeAllowed")
    number_of_questions : int = Field( alias = "numberOfQuestions")

    @validator("exam_title")
    def to_lowercase(cls, v):
        return v.lower().strip()

    class Config:
        allow_population_by_field_name = True


# Initialize Exam Session Model
class CreateExamSessionInput( BaseModel ):
	public_key : str =Field( alias= "publicKey")
	exam : str = Field( min_length = 16 )
	
	class Config:
		allow_population_by_field_name = True
		
		
		
# Resume a  Exam Session Model
class ResumeExamSessionInput( BaseModel ):
	public_key : str =Field( alias= "publicKey")
	
	
	class Config:
		allow_population_by_field_name = True



# Exam Session Response 
class ExamSessionResponse(BaseModel):
	id : str = Field( default_factory= gen_uid)
	session : str = Field( min_length = 16)
	question : str = Field( min_length = 16 )
	created : float = Field( min =0, default_factory = time )
	response : str = Field( min_length = 1)
	response_content : str = Field( min_length = 1 , alias = "responseContent")
	is_correct : bool = Field( default = False , alias = "isCorrect" )
	edits : int = Field( default  = 0 )
	integrity_hash : list[None,str]= Field( default = None , min_length = 32 , alias = "integrityHash" )
	
	class Config:
		allow_population_by_field_name = True
	


# Exam Session Model 

class ExamSession(BaseModel):
	peer_public_key : str =Field( alias= "peerPublicKey")
	public_key : str =Field( alias= "publicKey")
	private_key : str = Field( alias= "privateKey")
	id : str = Field( default_factory= gen_uid)
	exam : str = Field( min_length = 16 )
	user : str = Field(min_length = 16 )
	created : float = Field( min =0, default_factory = time )
	question_ids = list[str] = Fieldublic( min_items = 5, alias = "questionIds" )
	ping_interval : int = Field( default = 5 , alias = "pingInterval" )
	last_ping : Union[None,float] = Field( default  = None, min = 0, alias = "lastPing" )
	is_active : bool = Field( default = True, alias = "isActive" )
	submitted : bool = Field( default = False )
	
	
	class Config:
		allow_population_by_field_name = True
		
		
		
@method(name="exams.create_session")
async def create_exam_session(req):
	req = validate_req(req)

	user, payload = authenticate_user(req.auth)
	
	err, model = model_validate(CreateExamSessionInput, req.body)
	
	if err:
      return InvalidParams(err)



	
	
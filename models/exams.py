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



# Exam Session Response 
class ExamSessionResponse(BaseModel):
	id : str = Field( default_factory= gen_uid)
	session : str = Field( min_length = 16)
	question : str = Field( min_length = 16 )
	created : float = Field( min =0, default_factory = time )
	response_content : str = Field( min_length = 1 , alias = "responseContent")
	is_correct : bool = Field( default = False , alias = "isCorreeditsct" )
	edits : int = Field( default  = 0 )
	
	class Config:
		allow_population_by_field_name = True
	


# Exam Session Model 

class ExamSession(BaseModel):q
	id : str = Field( default_factory= gen_uid)
	exam : str = Field( min_length = 16 )
	user : str = Field(min_length = 16 )
	created : float = Field( min =0, default_factory = time )
	question_ids = list[str] = Field( min_items = 5, alias = "questionIds" )
	ping_interval : int = Field( default = 5 , alias = "pingInterval" )
	last_ping : Union[None,float] = Field( default  = None, min = 0, alias = "lastPing" )
	is_active : bool = Field( default = True, alias = "isActive" )
	submitted : bool = Field( default = False )
	
	
	class Config:
		allow_population_by_field_name = True
	
	
from pydantic import BaseModel, Field, HttpUrl, validator
from lib.utils import gen_uid
from typing import Union

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
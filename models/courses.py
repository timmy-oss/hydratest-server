from enum import Enum
from typing import Union
from time import time
from pydantic import BaseModel, Field, HttpUrl, validator

from lib.utils import gen_uid

class CreateCourseInputModel(BaseModel):
    id: str = Field(default_factory=gen_uid)
    course_title: str = Field(min_length=8, alias="courseTitle", )
    allow_public_contributions: bool = Field(alias="allowPublicContributions")
    course_cover: Union[HttpUrl, None] = Field(alias="courseCover", default=None)

    @validator("course_title")
    def to_lowercase(cls, v):
        return v.lower().strip()

    class Config:
        allow_population_by_field_name = True


class QuestionType(str, Enum):
    objective = "objective"
    germane = "germane"


class Options(str, Enum):
    a = "a"
    b = "b"
    c = "c"
    d = "d"


class CourseQuestion(BaseModel):
    id: str = Field(default_factory=gen_uid)
    question_type: QuestionType = Field(alias="questionType")
    question_content: str = Field(min_length=8, max_length=512, alias="questionContent")
    answer: Union[str, None] = Field(min_length=1, max_length=512, default=None)
    correct_option: Union[Options, None] = Field(alias="correctOption", default=None)
    option_A: Union[str, None] = Field(min_length=1, max_length=512, alias="optionA", default=None)
    option_B: Union[str, None] = Field(min_length=1, max_length=512, alias="optionB", default=None)
    option_C: Union[str, None] = Field(min_length=1, max_length=512, alias="optionC", default=None)
    option_D: Union[str, None] = Field(min_length=1, max_length=512, alias="optionD", default=None)
    lock_question: bool = Field(alias="lockQuestion")
    course: str
    illustration: Union[HttpUrl, None] = Field(default=None)
    upvotes : list[str]  = Field( default= [])
    downvotes : list[str] = Field( default= [])
    flags : list[str] = Field( default= [])
    created : float = Field( min =0, default_factory = time )
    last_updated : float = Field( min =0, default_factory = time , alias="lastUpdated")




    @validator("answer")
    def validate_answer(cls, v, values):

        if "question_type" in values and values["question_type"].value == QuestionType.germane.value:
            if not v:
                raise ValueError("value is required for a germane question")
            else:
                return v.strip().upper()

        # else:
        #     raise ValueError("question_type is not present")

    @validator("correct_option", "option_A", "option_B", "option_C", "option_D")
    def validate_options(cls, v, values):

        if "question_type" in values and values["question_type"].value == QuestionType.objective.value:
            if not v:
                raise ValueError("value is required for an objective question")
            else:
                return v.strip()

        # else:
        #     raise ValueError("question_type is not present")

    class Config:
        allow_population_by_field_name = True

from pydantic import BaseModel, Field, HttpUrl, validator
from lib.utils import gen_uid
from typing import Union

class CreateCourseInputModel(BaseModel):
    id : str = Field( default_factory= gen_uid)
    course_title : str = Field(min_length = 8, alias = "courseTitle", )
    allow_public_contributions : bool = Field(alias = "allowPublicContributions")
    course_cover : Union[HttpUrl,None]  = Field(alias = "courseCover", default= None)

    @validator("course_title")
    def to_lowercase(cls, v):
        return v.lower().strip()

    class Config:
        allow_population_by_field_name = True
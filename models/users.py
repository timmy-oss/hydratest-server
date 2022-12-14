from pydantic import BaseModel, Field, validator



class CreateUserModel(BaseModel):
    " User Model Creation Payload "

    firstname : str =  Field( min_length= 3, max_length  = 35)
    lastname : str =  Field( min_length= 3, max_length  = 35)
    password : str = Field( min_length= 8,max_length= 35)


    class Config:
        allow_population_by_field_name = True



class RefreshTokenModel(BaseModel):

    "Refresh an existing  jwt token"

    token :  str = Field(min_length= 64)






class AuthTokenModel(BaseModel):


    token :  str = Field(min_length= 64)




class LoginDataModel(BaseModel):
    " Model For Login Data "

    id : str = Field( min_length= 7, max_length= 7 )
    password : str = Field( min_length= 8, max_length= 35)


    @validator("id")
    def validate_id(cls, v):
        v = v.upper()

        if v[0] != "U":
            raise ValueError("invalid ID")

        if not  v[1:].isdigit():
            raise ValueError("invalid ID")

        return v


        

        


    
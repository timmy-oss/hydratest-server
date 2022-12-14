from pydantic import BaseSettings,BaseModel
from pydantic import AnyUrl
from typing import Any



class RequestModel(BaseModel):
    " Format for request object"

    auth : Any
    body : Any




class Settings(BaseSettings):
    " Model for the application settings  "
    debug : bool = True
    app_name : str = "HydraTest"
    allowed_origins : list[str] = ["http://localhost:3000"]
    db_url : AnyUrl = "redis://127.0.0.1:10005"
    db_username : str = "default"
    db_password  : str = "root"
    jwt_secret : str = "jwt_secret"
    jwt_exp_in_mins : int = 30



    class Meta:
        env_file = ".secrets"
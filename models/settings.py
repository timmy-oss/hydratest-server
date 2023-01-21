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
    ping_interval : int = 2
    allowed_origins : list[str] = ["http://localhost:3000","https://hydratest.vercel.app"]
    db_url : AnyUrl = "redis://127.0.0.1:10005"
    db_username : str = "default"
    db_password  : str = "root"
    jwt_secret : str = "jwt_secret"
    jwt_exp_in_mins : int = 120
    ipfs_node_url: str = 'https://ipfs.infura.io:5001'
    infura_project_id  :str = ""
    infura_project_secret : str = ""
    ipfs_read_node : str = ""



    class Config:
        env_file = ".secrets"
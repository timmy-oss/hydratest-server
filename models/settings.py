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
    ping_interval : int = 5
    allowed_origins : list[str] = ["http://localhost:3000","https://timmy-oss-sturdy-bassoon-x47x4vqv4q536vjw-3000.preview.app.github.dev"]
    db_url : AnyUrl = "redis://127.0.0.1:10005"
    db_username : str = "default"
    db_password  : str = "root"
    jwt_secret : str = "jwt_secret"
    jwt_exp_in_mins : int = 120
    ipfs_node_url: str = 'https://ipfs.infura.io:5001'
    infura_project_id  :str = "2CASClsLixgaD7e6qlO5LfIYA4b"
    infura_project_secret : str = "3a6dfcb5e77b97ba69b90f55e1f7b326"
    ipfs_read_node : str = "https://fabaaw.infura-ipfs.io/ipfs"



    class Config:
        env_file = ".secrets"
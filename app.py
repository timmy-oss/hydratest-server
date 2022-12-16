
import methods
from fastapi import FastAPI, Request,Response,UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.settings import Settings
from jsonrpcserver import async_dispatch
from lib.ipfs import upload_to_ipfs


app_settings = Settings()



app = FastAPI( debug= app_settings.debug, title=  app_settings.app_name, description= "The ultimate test platform.", version= "0.1.0" )



app.add_middleware(
    CORSMiddleware,
    allow_origins= app_settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)




# RPC endpoint

@app.post("/api/v1/rpc")
async def rpc( request : Request ):
    return Response( await async_dispatch(await request.body()))



@app.post("/api/v1/upload")
async def upload( upload_file : UploadFile = Form()):
    
    # MAX_FILE_SIZE = 1024 * 1024 * 3

    SUPPORTED_FORMATS = [
        "image/jpg",
        "image/jpeg",
        "image/webp",
        "image/png",
    ]


    if SUPPORTED_FORMATS.count(upload_file.content_type) == 0:
        raise HTTPException(
            status_code=400, detail="invalid content type for file")

    res = upload_to_ipfs( upload_file.file)

    return res

   





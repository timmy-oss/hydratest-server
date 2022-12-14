
from fastapi import FastAPI, Request,Response
from fastapi.middleware.cors import CORSMiddleware
from models.settings import Settings
from jsonrpcserver import async_dispatch
import methods


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





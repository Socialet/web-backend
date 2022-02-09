import uvicorn
from fastapi import FastAPI
from fastapi.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from app.config import application_shutdown

from app.api import app_api

middleware = [Middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])]

app = FastAPI(
    title="SMWT",
    version="1.0",
    description="All in one Social Media Workflow Tool",
    middleware=middleware
) 

@app.on_event("shutdown")
def shutdown_event():
    application_shutdown()


app.include_router(app_api,prefix="/api",tags=["ALL API"])

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000, log_level='info')
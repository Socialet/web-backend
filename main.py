import uvicorn
from app.api import app_api
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="SMWT",
    version="1.0",
    description="All in one Social Media Workflow Tool",
)

origins = ['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_api,prefix="/api",tags=["ALL API"])

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000, log_level='info')
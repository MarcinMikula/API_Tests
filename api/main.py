from fastapi import FastAPI
from api.routes import rest_api
from api.database.db_utils import init_db

app = FastAPI()

app.include_router(rest_api.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {"message": "Welcome to the Online Store API"}
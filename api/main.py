from fastapi import FastAPI

from routes.users import users_router
from routes.registration import registration_router

api = FastAPI()

api.include_router(users_router)
api.include_router(registration_router)

@api.get("/")
async def root():
    return {"message": "Hello world"}


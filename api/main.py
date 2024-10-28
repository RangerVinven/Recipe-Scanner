from fastapi import FastAPI

from routes.users import users_router
from routes.steps import steps_router
from routes.recipes import recipes_router
from routes.ingredients import ingredients_router 
from routes.registration import registration_router

api = FastAPI()

api.include_router(users_router)
api.include_router(registration_router)
api.include_router(recipes_router)
api.include_router(steps_router)
api.include_router(ingredients_router)

@api.get("/")
async def root():
    return {"message": "Hello world"}


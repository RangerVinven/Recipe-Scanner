from fastapi import APIRouter
from sqlalchemy import insert

from models.tables import users_table
from utils.string_manipulator import hash_string
from utils.database_connector import connection

users_router = APIRouter(prefix="/users")

# Lists the users (for development only)
@users_router.get("/all")
async def get_users():
    # Selects all the users
    users = users_table.select()
    results = connection.execute(users).mappings().all()

    return results

# Lists a user's data
@users_router.get("/")
async def get_user():
    return {"user": "root"}

# Deletes a user
@users_router.delete("/")
async def delete_user():
    return {"user": "root"}

# Updates a user
@users_router.patch("/")
async def update_user():
    return {"user": "root"}

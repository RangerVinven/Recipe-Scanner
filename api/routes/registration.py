import secrets

from fastapi import APIRouter, HTTPException, Response, Request
from sqlalchemy import select, insert, update, delete

from models.users import CreateUser, Login
from models.tables import users_table, session_tokens_table

from utils.database_connector import connection
from utils.string_manipulator import hash_string
from utils.query_manager import insert_data
from utils.request_manager import get_session_token

registration_router = APIRouter()

# Creates the session token and saves it to the database
async def create_session_token(user_id):
    session_token = secrets.token_hex()

    insert_query = insert(session_tokens_table).values(User_ID=user_id, Session_Token=session_token)
    connection.execute(insert_query)
    connection.commit()

    return session_token

@registration_router.post("/login")
async def login(login_data: Login, response: Response):

    # Hashes the password
    login_data.Password = hash_string(login_data.Password) 
    
    # Searches the table for a matching email and password
    select_query = select(users_table).where((users_table.c.Email == login_data.Email) & (users_table.c.Password == login_data.Password))
    results = connection.execute(select_query)
    num_of_results = results.rowcount

    # If there email or password is incorrect
    if num_of_results == 0:
        raise HTTPException(status_code=401, detail="Invalid email or password")
        return

    # Gets the logged-in user's info as an array of dictionaries
    user = results.mappings().all()[0]
    user_id = user["User_ID"]

    # Creates the session_token and saves it to the database
    session_token = await create_session_token(user_id)

    response.set_cookie(key="session_token", value=session_token)
    return 

# Creates a user 
@registration_router.post("/sign_up")
async def create_user(user: CreateUser, response: Response):

    # Hashes the password
    user.Password = hash_string(user.Password)

   # Inserts the user, and does the error handling
    user_id = await insert_data(users_table, user)

    # Creates the session_token and saves it to the database
    session_token = await create_session_token(user_id)

    response.set_cookie(key="session_token", value=session_token)
    return 

# Signs the user out
@registration_router.delete("/logout")
async def logout(request: Request, response: Response):
    # Returns the session tokens from the request
    session_token = get_session_token(request)

    # Deletes the session token from the session_tokens table
    delete_query = delete(session_tokens_table).where(session_tokens_table.c.Session_Token == session_token)
    result = connection.execute(delete_query)
    connection.commit()

    if result.rowcount > 0:
        response.delete_cookie(key="session_token")
        return 

    else:
        raise HTTPException(status_code=500, detail="Something went wrong")
        return

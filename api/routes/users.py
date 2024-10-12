from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select, insert, delete, update

from models.tables import users_table, session_tokens_table
from models.users import UpdateUser

from utils.string_manipulator import hash_string
from utils.database_connector import connection
from utils.query_manager import join_tables_query
from utils.request_manager import get_session_token

users_router = APIRouter(prefix="/users")

# Lists the users (for development only)
# @users_router.get("/all")
# async def get_users():
#     # Selects all the users
#     users = users_table.select()
#     results = connection.execute(users).mappings().all()
#
#     return results

# Lists a user's data
@users_router.get("/")
async def get_user(request: Request):
    session_token = get_session_token(request)

    # Joins the Users and Session_Tokens tables and finds the data of the current user    
    table_join =  join_tables_query(session_tokens_table, session_tokens_table.c.User_ID, users_table, users_table.c.User_ID)
    select_query = select(users_table.c.First_Name, users_table.c.Email, users_table.c.Preferred_Units).select_from(table_join).where(session_tokens_table.c.Session_Token == session_token)

    user_data = connection.execute(select_query).first()
        
    return { "First_Name": user_data[0], "Email": user_data[1], "Preferred_Units": user_data[2] }

# Deletes a user
@users_router.delete("/")
async def delete_user(request: Request):
    session_token = get_session_token(request)

    try:
        # Joins the tables and finds the user ID
        table_join =  join_tables_query(session_tokens_table, session_tokens_table.c.User_ID, users_table, users_table.c.User_ID)
        select_query = select(users_table.c.User_ID).select_from(table_join).where(session_tokens_table.c.Session_Token == session_token)

        results = connection.execute(select_query)
        user_id = results.first()[0]

        # Deletes the user 
        delete_query = users_table.delete().where(users_table.c.User_ID == user_id)
        num_of_results_changed = connection.execute(delete_query).rowcount
        connection.commit()

        if num_of_results_changed > 0:
            return

        else:
            raise HTTPException(status_code=400, detail="Couldn't delete user")

    except:
        raise HTTPException(status_code=400, detail="Couldn't delete user")

    return 

# Updates a user
@users_router.patch("/")
async def update_user(update_data: UpdateUser, request: Request):
    session_token = get_session_token(request)

    # Joins the tables and finds the user ID
    table_join =  join_tables_query(session_tokens_table, session_tokens_table.c.User_ID, users_table, users_table.c.User_ID)
    select_query = select(users_table.c.User_ID).select_from(table_join).where(session_tokens_table.c.Session_Token == session_token)
    results = connection.execute(select_query)

    # Gets the user's ID
    user_id = results.first()[0]

    # Changes removes the None values from the dictionary
    # Removes none values from the user's data,
    # Taken from: https://blog.finxter.com/5-best-ways-to-remove-null-values-from-a-python-dictionary/
    data = {k: v for k, v in vars(update_data).items() if v is not None}

    # Hashes the password if it's part of the update_data 
    if data.get("Password") is not None:
       data["Password"] = hash_string(data["Password"])

    # Updates the user's data
    update_query = update(users_table).where(users_table.c.User_ID == user_id).values(data)
    connection.execute(update_query)

    connection.commit()

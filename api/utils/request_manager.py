from fastapi import Request
from sqlalchemy import select

from utils.query_manager import join_tables_query
from utils.database_connector import connection

from models.tables import session_tokens_table, users_table

# Gets the session token from the user's request
def get_session_token(request: Request):
    cookies = request.cookies 
    return cookies["session_token"]

def get_user_id(session_token):
    # Joins the tables and finds the user ID
    table_join =  join_tables_query(session_tokens_table, session_tokens_table.c.User_ID, users_table, users_table.c.User_ID)
    select_query = select(users_table.c.User_ID).select_from(table_join).where(session_tokens_table.c.Session_Token == session_token)

    results = connection.execute(select_query)
    user_id = results.first()[0]

    return user_id

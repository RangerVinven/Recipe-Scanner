from fastapi import Request

# Gets the session token from the user's request
def get_session_token(request: Request):
    cookies = request.cookies 
    return cookies["session_token"]

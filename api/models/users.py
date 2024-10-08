from pydantic import BaseModel

class CreateUser(BaseModel):
    First_Name: str
    Email: str
    Password: str
    Preferred_Units: str

class Login(BaseModel):
    Email: str
    Password: str

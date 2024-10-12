from pydantic import BaseModel 
from typing import Optional

class CreateUser(BaseModel):
    First_Name: str
    Email: str
    Password: str
    Preferred_Units: str

class Login(BaseModel):
    Email: str
    Password: str

class UpdateUser(BaseModel):
    First_Name: Optional[str] = None
    Email: Optional[str] = None
    Password: Optional[str] = None
    Preferred_Units: Optional[str] = None

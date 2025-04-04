from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.utils.constant.globals import UserRole

class Login(BaseModel):
	email : str
	password : str

class MyUser(BaseModel):
	email : str
	password : str
	name: str

class User(MyUser):
	id :str

class Token(BaseModel):
	access_token : str
	token_type : str
	role : UserRole


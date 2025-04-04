from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.utils.constant.globals import UserRole

class MyUser(BaseModel):
	email : str
	password : str

class Token(BaseModel):
	access_token : str
	token_type : str
	role : UserRole


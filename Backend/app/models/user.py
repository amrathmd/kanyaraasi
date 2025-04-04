from sqlalchemy import Column, String, Enum
from enum import Enum as PythonEnum

from app.core.database import Base
from .common import CommonModel
from app.utils.constant.globals import UserRole

class User(Base):
	__tablename__ = "users"

	id = Column(String,unique=True,primary_key=True)
	email = Column(String, unique=True)
	password = Column(String)
	role = Column(Enum(UserRole), default=UserRole.USER)

	def __repr__(self):
		return f"{self.email}"
	
metadata = Base.metadata


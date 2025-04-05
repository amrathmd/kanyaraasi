from pydantic import BaseModel


class AccountUpdate(BaseModel):
    available_balance: float

class AccountCreate(BaseModel):
    total_balance: float
    available_balance: float

class AccountResponse(BaseModel):
    user_id: str
    year: str
    total_balance: float
    available_balance: float

    class Config:
        orm_mode = True
from datetime import datetime

from fastapi import Depends, HTTPException

from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.models.account import Account
from sqlalchemy import update

AWS_REGION = "us-east-1"

def update_account_balance(
        user_id: str,
        available_balance: int,
        spent_amount: int,
        year: str = str(datetime.now().year),
        db: Session = Depends(get_db)
):
    stmt = update(Account).where(Account.user_id == user_id, Account.year == year).values(available_balance=available_balance - spent_amount)
    result = db.execute(stmt)
    db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": f"Available balance updated for user '{user_id}' in '{year}'"}

def get_account_balance(db:Session ,user_id:str):
    account_details = db.query(Account).filter(Account.user_id == user_id).first()
    return {
        "available_balance" : account_details.available_balance,
        "total_balance" : account_details.total_balance
    }
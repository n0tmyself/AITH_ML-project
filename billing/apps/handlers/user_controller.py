from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import BalanceHistory, UserModel
from . import auth
from .logger import logger

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/balance")
async def get_balance(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
):
    user = db.query(UserModel).filter(UserModel.email == current_user.email).first()
    logger.info(f"User {user.email} has balance: {user.balance}")
    return {"email": user.email, "balance": user.balance, "name": user.name}


@router.post("/balance")
def update_balance(
    amount: float,
    db: Session = Depends(get_db),
    curerent_user: UserModel = Depends(auth.get_current_user),
):
    try:
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")

        user = (
            db.query(UserModel).filter(UserModel.email == curerent_user.email).first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.balance += amount
        db.commit()

        balance_history = BalanceHistory(
            user_id=user.id,
            amount=amount,
            operation_type="add",
        )
        db.add(balance_history)
        db.commit()

        db.refresh(user)
        logger.info(f"User {user.email} has new balance: {user.balance}")
        return {
            "amount": amount,
            "new_balance": user.balance,
            "message": "Balance updated",
        }

    except HTTPException as He:
        raise He
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating balance: {str(e)}")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..broker.tasks import generate_text_task
from ..db.database import get_db
from ..db.models import BalanceHistory, GenerationModel, TariffModel, TaskStatus, UserModel
from ..db.schemas import GenerationRequest, GenerationResponse
from . import auth

router = APIRouter(prefix="/model", tags=["Model"])


@router.post("/generate", response_model=GenerationResponse)
async def generate(
    request: GenerationRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_user),
):
    user = db.query(UserModel).filter(UserModel.email == current_user.email).first()

    cost = TariffModel.get_cost(request.tariff)
    if cost == 0:
        raise HTTPException(status_code=400, detail="Invalid tariff type")

    if user.balance < cost:
        raise HTTPException(status_code=402, detail="Insufficient funds")

    result = generate_text_task(request.prompt, request.tariff)
    task = generate_text_task.delay(request.prompt, request.tariff)
    task_id = task.id

    try:
        user.balance -= cost

        generation = GenerationModel(
            user_id=user.id,
            task_id=task_id,
            promt=request.prompt,
            result=result,
            tariff=request.tariff,
            cost=cost,
            status=False,
        )

        db.add(generation)
        db.flush()

        task_status = TaskStatus(user_id=user.id, task_id=task_id)
        db.add(task_status)

        balance_history = BalanceHistory(
            user_id=user.id,
            amount=-cost,
            operation_type="spend",
            description=f"Generation using {request.tariff} model",
        )
        db.add(balance_history)

        db.commit()

        return GenerationResponse(
            task_id=task_id,
            result=result,
            cost=cost,
            remaining_balance=user.balance,
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

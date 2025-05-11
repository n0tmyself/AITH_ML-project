from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from core.use_cases.billing_use_cases import BillingService
from infra.web.dependencies.billing_dependencies import get_billing_service
from infra.message_broker.producer import RabbitMQProducer
from infra.message_broker.schemas import TextGenerationTask
import logging

router = APIRouter(prefix="/billing", tags=["billing"])
logger = logging.getLogger(__name__)

class ChargeRequest(BaseModel):
    user_id: str
    cost: int

@router.post("/charge")
async def charge(
    request: ChargeRequest,
    billing_service: BillingService = Depends(get_billing_service),
):
    """Заглушка для списания средств. В реальности будет работать через RabbitMQ."""
    logger.info(f"Списание средств: user_id={request.user_id}, cost={request.cost}")
    
    # заглушка
    return {
        "status": "ok",
        "message": "Средства списаны (заглушка)",
        "user_id": request.user_id,
        "cost": request.cost,
    }
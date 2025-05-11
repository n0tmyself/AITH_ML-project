from fastapi import Depends
from sqlalchemy.orm import Session
from infra.db.database import get_db
from infra.db.billing_repository_impl import BillingRepositoryImpl
from core.use_cases.billing_use_cases import BillingService

def get_billing_service(db: Session = Depends(get_db)) -> BillingService:
    repository = BillingRepositoryImpl(db)
    return BillingService(repository)

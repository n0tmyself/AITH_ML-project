from fastapi import Depends
from sqlalchemy.orm import Session
from infra.db.database import get_db
from infra.db.user_repository_impl import UserRepositoryImpl
from infra.db.billing_repository_impl import BillingRepositoryImpl
from core.use_cases.user_use_cases import UserService

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    user_repo = UserRepositoryImpl(db)
    billing_repo = BillingRepositoryImpl(db)
    return UserService(user_repo, billing_repo)

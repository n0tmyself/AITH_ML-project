from typing import Optional
from core.entities.user import User
from core.entities.billing import BillingAccount
from core.repositories.user_repository import UserRepository
from core.repositories.billing_repository import BillingRepository

class UserService:
    def __init__(self, user_repo: UserRepository, billing_repo: BillingRepository):
        self.user_repo = user_repo
        self.billing_repo = billing_repo

    def register_user(self, user: User):
        self.user_repo.save(user)

        billing_account = BillingAccount(user_id=user.id, credits=0)
        self.billing_repo.save(billing_account)
        
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)

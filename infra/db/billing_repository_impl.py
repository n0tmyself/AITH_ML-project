from sqlalchemy.orm import Session
from core.entities.billing import BillingAccount
from core.repositories.billing_repository import BillingRepository
from infra.db.models import BillingAccountModel

class BillingRepositoryImpl(BillingRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_user_id(self, user_id: str) -> BillingAccount:
        model = self.db.query(BillingAccountModel).filter_by(user_id=user_id).first()
        if not model:
            model = BillingAccountModel(user_id=user_id, credits=0)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
        return BillingAccount(user_id=model.user_id, credits=model.credits)

    def save(self, account: BillingAccount):
        model = self.db.query(BillingAccountModel).filter_by(user_id=account.user_id).first()
        if not model:
            # запасной случай — не должен возникать, но пусть будет
            model = BillingAccountModel(user_id=account.user_id, credits=account.credits)
            self.db.add(model)
        else:
            model.credits = account.credits
        self.db.commit()

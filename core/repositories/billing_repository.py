from abc import ABC, abstractmethod
from core.entities.billing import BillingAccount

class BillingRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: str) -> BillingAccount:
        pass

    @abstractmethod
    def save(self, account: BillingAccount):
        pass

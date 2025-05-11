from core.repositories.billing_repository import BillingRepository

class BillingService:
    def __init__(self, billing_repository: BillingRepository):
        self.billing_repository = billing_repository

    def charge_for_prediction(self, user_id: str, cost: int):
        account = self.billing_repository.get_by_user_id(user_id)
        account.charge(cost)
        self.billing_repository.save(account)

    def top_up_account(self, user_id: str, amount: int):
        account = self.billing_repository.get_by_user_id(user_id)
        account.add_credits(amount)
        self.billing_repository.save(account)

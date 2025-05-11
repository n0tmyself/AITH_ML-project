from dataclasses import dataclass

@dataclass
class BillingAccount:
    user_id: str
    credits: int

    def charge(self, amount: int):
        if amount > self.credits:
            raise ValueError("Недостаточно кредитов")
        self.credits -= amount

    def add_credits(self, amount: int):
        self.credits += amount

from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey
from infra.db.database import Base

class UserModel(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    

class BillingAccountModel(Base):
    __tablename__ = "billing_accounts"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True, index=True)
    credits = Column(Integer, nullable=False, default=0)

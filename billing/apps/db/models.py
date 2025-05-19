from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing_extensions import List, Optional

from .database import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    balance: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    generations: Mapped[List["GenerationModel"]] = relationship(
        "GenerationModel", back_populates="user"
    )
    balance_history: Mapped[List["BalanceHistory"]] = relationship(
        "BalanceHistory", back_populates="user"
    )


class BalanceHistory(Base):
    __tablename__ = "balance_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    amount: Mapped[float] = mapped_column(Float)
    operation_type: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    description : Mapped[str] = mapped_column(String, nullable=True)
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="balance_history"
    )


class GenerationModel(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    task_id: Mapped[str] = mapped_column(String)
    status: Mapped[bool] = mapped_column(Boolean)
    tariff: Mapped[str] = mapped_column(String)
    promt: Mapped[str] = mapped_column(Text)
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cost: Mapped[float] = mapped_column(Float)
    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    processing_time: Mapped[float] = mapped_column(Float, nullable=True)

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="generations")


class TaskStatus(Base):
    __tablename__ = "TaskStatus"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer)
    task_id: Mapped[str] = mapped_column(String)


class TariffModel(Base):
    __tablename__ = "tariffs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    cost: Mapped[float] = mapped_column(Float)

    @staticmethod
    def get_cost(tarriff_name: str) -> float:
        tariffs = {
            "lite": 5.0,
            "max": 20.0,
        }
        return tariffs.get(tarriff_name, 0.0)

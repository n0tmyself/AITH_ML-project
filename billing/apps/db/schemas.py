from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, constr
from typing_extensions import Annotated, List


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: Annotated[str, constr(min_length=4)]


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserJWT(BaseModel):
    name: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_date: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    model_config = ConfigDict(json_encoders={str: str})
    access_token: str
    token_type: str


class BillingAccountResponse(BaseModel):
    user_id: int
    balance: float
    model_config = ConfigDict(from_attributes=True)


class BillingUpdateRequest(BaseModel):
    amount: float


class GenerationCreate(BaseModel):
    user_id: int
    tariff: str
    promt: Annotated[str, constr(min_length=1, max_length=1000)]


class TariffResponse(BaseModel):
    id: int
    name: str
    cost: float

    model_config = ConfigDict(from_attributes=True)


class GenerationRequest(BaseModel):
    model_config = ConfigDict(json_encoders={str: str})
    prompt: Annotated[str, constr(min_length=1, max_length=1000)]
    tariff: str


class GenerationResponse(BaseModel):
    model_config = ConfigDict(json_encoders={str: str})
    task_id: str
    result: str
    cost: float
    remaining_balance: float


class GenerationListResponse(BaseModel):
    generations: List[GenerationResponse]
    total_count: int

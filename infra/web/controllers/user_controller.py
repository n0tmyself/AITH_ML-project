from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from core.entities.user import User
from infra.db.user_repository_impl import UserRepositoryImpl
from infra.web.dependencies.user_dependencies import get_user_service

router = APIRouter(prefix="/users", tags=["users"])

class RegisterRequest(BaseModel):
    id: str
    name: str
    email: Optional[str] = None

@router.post("/register")
async def register(
    request: RegisterRequest,
    user_service = Depends(get_user_service),
):
    existing_user = user_service.get_user_by_id(request.id)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким id уже зарегистрирован")

    user = User(id=request.id, name=request.name, email=request.email)
    user_service.register_user(user)
    return {"status": "registered"}
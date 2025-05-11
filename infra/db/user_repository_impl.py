from sqlalchemy.orm import Session
from core.repositories.user_repository import UserRepository
from core.entities.user import User
from infra.db.models import UserModel
from infra.db.mappers import user_model_to_entity, user_entity_to_model

class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, user: User):
        user_model = user_entity_to_model(user)
        self.db.add(user_model)
        self.db.commit()
        
    def get_by_id(self, user_id: str) -> User | None:
        user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if user_model:
            return user_model_to_entity(user_model)
        return None
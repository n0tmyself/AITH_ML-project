from core.entities.user import User
from infra.db.models import UserModel

def user_model_to_entity(model: UserModel) -> User:
    return User(id=model.id, name=model.name, email=model.email)

def user_entity_to_model(user: User) -> UserModel:
    return UserModel(id=user.id, name=user.name, email=user.email)

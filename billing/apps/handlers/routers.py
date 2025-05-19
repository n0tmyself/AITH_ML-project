from .auth import router as auth_router
from .model import router as model_router
from .user_controller import router as user_router

all_routers = [auth_router, model_router, user_router]

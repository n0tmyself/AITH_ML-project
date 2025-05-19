import datetime
import os

from dotenv import load_dotenv
from fastapi import APIRouter, Cookie, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from typing_extensions import Annotated, Optional

from ..db.database import get_db
from ..db.models import UserModel
from ..db.schemas import Token, UserCreate, UserLogin
from .logger import logger

# import jwt

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

security = HTTPBearer()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_user(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()


def create_token(email: str):
    toke_payload = {
        "sub": email,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))),
    }
    token = jwt.encode(toke_payload, SECRET_KEY, algorithm="HS256")
    return token


async def get_current_user(
    token: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    cookie_token: Optional[str] = Cookie(
        default=None, alias=os.getenv("TOKEN_COOKIE_NAME")
    ),
    db: Session = Depends(get_db),
) -> str:
    credentials = token.credentials if token else cookie_token
    if not credentials:
        raise HTTPException(status_code=401, detail="Token not provided")

    try:
        payload = jwt.decode(credentials, SECRET_KEY, algorithms="HS256")
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401, detail="Invalid token: username not found"
            )

        user = get_user(db, email)
        return user
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token decode error: {e}")


@router.post("/register")
async def register_user(user_f: UserCreate, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == user_f.email).first()

    if user is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hash(user_f.password)

    db_user = UserModel(
        name=user_f.name,
        email=user_f.email,
        password=hashed_password,
        created_date=datetime.datetime.now(),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"User: {user_f.name} registered")

    return {"message": f"User: '{user_f.name}' created"}


@router.post("/login", response_model=Token)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    email = user.email
    password = user.password

    db_user = db.query(UserModel).filter(UserModel.email == email).first()

    if db_user is None:
        logger.info(f"User with email {email} not registered")
        raise HTTPException(status_code=401, detail="Login failed: user not found")

    if not bcrypt.verify(password, db_user.password):
        logger.info(f"User {email} provided incorrect password")
        raise HTTPException(status_code=401, detail="Login failed: incorrect password")

    db.commit()

    token = create_token(db_user.email)
    logger.info(f"User {email} logged in")
    return {"access_token": token, "token_type": "bearer"}

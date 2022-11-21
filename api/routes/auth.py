import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..schemas import Login, Token, db
from ..utils.auth2 import create_access_token
from ..utils.utils import verify_password

router = APIRouter(prefix="/login", tags=["Authentication"])


async def authenticate_user(db, email: str, password: str):
    user = await db["users"].find_one({"email": email})
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user


@router.post("", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    email = user_credentials.username
    password = user_credentials.password.strip()
    user = await authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"id": user["_id"]})
    return {"access_token": access_token, "token_type": "bearer"}

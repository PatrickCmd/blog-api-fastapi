import secrets

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from ..schemas import User, UserResponse, db
from ..utils.auth2 import get_current_user
from ..utils.send_email import send_registration_email
from ..utils.utils import get_password_hash, verify_password

router = APIRouter(tags=["User Routes"])


@router.post(
    "/registration",
    response_description="Register a user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registration(user_info: User, background_tasks: BackgroundTasks):
    user_info = jsonable_encoder(user_info)

    # check for duplicates
    username_found = await db["users"].find_one({"name": user_info["name"]})
    email_found = await db["users"].find_one({"email": user_info["email"]})

    if username_found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )

    if email_found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    # hash user password
    user_info["password"] = get_password_hash(user_info["password"])
    # create user apikey
    user_info["apikey"] = secrets.token_hex(32)

    # create new user
    new_user = await db["users"].insert_one(user_info)
    created_user = await db["users"].find_one({"_id": new_user.inserted_id})

    # send registration email to user
    subject = "Registration Successful"
    email_to = user_info["email"]
    body = {
        "title": "Registration Successful",
        "name": user_info["name"],
    }
    await send_registration_email(subject, email_to, body, background_tasks)

    return created_user


@router.get(
    "/users/me/",
    response_description="Get current user",
    response_model=UserResponse,
)
async def get_users_me(current_user: User = Depends(get_current_user)):
    return current_user

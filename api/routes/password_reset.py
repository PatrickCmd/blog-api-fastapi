from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException, Query,
                     Request, status)

from ..schemas import NewPassword, PasswordReset, UserResponse, db
from ..utils.auth2 import create_access_token, get_current_user
from ..utils.send_email import send_password_reset_email
from ..utils.utils import get_password_hash

router = APIRouter(
    prefix="/password",
    tags=["Password reset"],
)


@router.post("/reset-email", response_description="Reset user password request")
async def password_reset_request(
    user_email: PasswordReset, background_tasks: BackgroundTasks, request: Request
):
    user = await db["users"].find_one({"email": user_email.email})
    user_not_found_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User with this email account is not registered on our servers.",
    )

    if user is not None:
        token = create_access_token({"id": user["_id"]})

        base_url = request.base_url._url
        reset_link = f"{base_url}password/reset?token={token}"

        # Send password reset email
        subject = "Password Reset Request"
        email_to = user["email"]
        body = {
            "title": "Password Reset",
            "name": user["name"],
            "reset_link": reset_link,
        }
        await send_password_reset_email(subject, email_to, body, background_tasks)
        return {
            "message": "A password reset email has been sent to your email address."
        }
    else:
        raise user_not_found_exception


@router.put(
    "/reset", response_description="Reset user password", response_model=UserResponse
)
async def password_reset(new_password: NewPassword, token: str = Query(default=...)):
    request_data = {k: v for k, v in new_password.dict().items() if v is not None}

    request_data["password"] = get_password_hash(request_data["password"])

    if len(request_data) >= 1:
        current_user = await get_current_user(token)
        update_result = await db["users"].update_one(
            {"_id": current_user["_id"]},
            {"$set": request_data},
        )

        if update_result.modified_count == 1:
            updated_user = await db["users"].find_one({"_id": current_user["_id"]})
            return updated_user
        else:
            existing_user = await db["users"].find_one({"_id": current_user["_id"]})
            return existing_user
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User information not found on the server. Please confirm that the password reset provided is still valid",
        )

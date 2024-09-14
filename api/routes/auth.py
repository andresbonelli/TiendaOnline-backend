from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Response
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from passlib.exc import UnknownHashError

from ..models import (
    UserRegisterData,
    UserLoginData,
    UserUpdateData,
    PrivateUserFromDB,
    UserVerifyRequest,
    UserResetPasswordRequest
)
from ..services import (
    UsersServiceDependency,
    AuthServiceDependency,
    SecurityDependency,
    RefreshCredentials,
    send_account_verification_email,
    send_reset_password_email
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user: UserRegisterData,
    users: UsersServiceDependency,
    auth: AuthServiceDependency,
    background_tasks: BackgroundTasks
):
    user.role = "customer"
    hash_password = auth.get_password_hash(user.password)

    result = users.create_one(user, hash_password)
    if new_user := users.get_one(id=result.inserted_id, with_password=True):
        await send_account_verification_email(new_user, background_tasks=background_tasks)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error ocurred while retrieving new user to database."
        )
    return {"result message": f"User created with id: {result.inserted_id}"}

@auth_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user_account(
    verify_request: UserVerifyRequest,
    users: UsersServiceDependency,
    auth: AuthServiceDependency,
):
    user_from_db = users.get_one(email=verify_request.email, with_password=True)
    
    if user_from_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already verified"
        )

    context_time: datetime = user_from_db.modified_at or user_from_db.created_at 
    context_string = f"{user_from_db.hash_password}{context_time.strftime('%d/%m/%Y,%H:%M:%S')}-verify" 
    try:
        if auth.verify_password(context_string, verify_request.token):
            return users.update_one(
                user_from_db.id,
                UserUpdateData(is_active=True)
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Link expired or invalid"
            )
    except UnknownHashError:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a valid token"
            )
        
@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login_with_cookie(
    user: UserLoginData,
    response: Response,
    users: UsersServiceDependency,
    auth: AuthServiceDependency,
):
    user_from_db = users.get_one(username=user.username, with_password=True)
    if not user_from_db or not user_from_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist or inactive"
            )
    return auth.login_and_set_access_token(
        password=user.password,
        user_from_db=user_from_db,
        response=response
    )

@auth_router.get("/authenticated_user", status_code=status.HTTP_200_OK)
async def read_current_user(security: SecurityDependency):
    return dict(
        id=security.auth_user_id,
        username=security.auth_user_name,
        email=security.auth_user_email,
        role=security.auth_user_role,
        created_at=security.auth_user_created_at,
        modified_at=security.auth_user_modified_at,
        is_active=security.auth_user_is_active,
        address=security.auth_user_address
    )

@auth_router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_credentials(response: Response, auth: AuthServiceDependency, refresh: RefreshCredentials):
    return auth.refresh_access_token(response, refresh)

@auth_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def user_forgot_password(email: EmailStr, users: UsersServiceDependency, background_tasks: BackgroundTasks):
    user_from_db: PrivateUserFromDB = users.get_one(email=email, with_password=True)
    if not user_from_db or not user_from_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist or inactive"
            )
    await send_reset_password_email(user_from_db, background_tasks=background_tasks)
    return JSONResponse({"message": f"An email with password reset link has been sent to {email}"})

@auth_router.put("/reset-password", status_code=status.HTTP_200_OK)
async def user_reset_password(
    verify_request: UserResetPasswordRequest,
    auth: AuthServiceDependency,
    users: UsersServiceDependency
):
    user_from_db: PrivateUserFromDB = users.get_one(email=verify_request.email, with_password=True)
    if not user_from_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account has been suspended. Please contact support"
        )
        
    context_string = f"{user_from_db.hash_password}{user_from_db.modified_at.strftime('%d/%m/%Y,%H:%M:%S')}-reset-password" 
    try:
        if auth.verify_password(context_string, verify_request.token):
            return users.update_password(
                user_from_db.id,
                auth.get_password_hash(verify_request.new_password)
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Link expired or invalid"
            )
    except UnknownHashError:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not a valid token"
            )

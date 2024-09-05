from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Response

from ..models import UserRegisterData, UserLoginData, UserUpdateData, PrivateUserFromDB, UserVerifyRequest
from ..services import UsersServiceDependency, AuthServiceDependency, SecurityDependency, RefreshCredentials, send_account_verification_email


auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.post("/register")
async def register(user: UserRegisterData,
                   users: UsersServiceDependency,
                   auth: AuthServiceDependency,
                   background_tasks: BackgroundTasks):
    hash_password = auth.get_password_hash(user.password)
    result = users.create_one(user, hash_password)
    fresh_user = users.get_one(id=result.inserted_id, with_password=True)
    
    await send_account_verification_email(PrivateUserFromDB.model_validate(fresh_user), background_tasks=background_tasks)
    
    return {"result message": f"User created with id: {result.inserted_id}"}

@auth_router.post("/verify")
async def verify_user_account(verify_request: UserVerifyRequest,
                              users: UsersServiceDependency,
                              auth: AuthServiceDependency,
):
    user_from_db = PrivateUserFromDB.model_validate(
        users.get_one(email=verify_request.email, with_password=True)
        )
    if user_from_db.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account already verified"
        )

    context_time: datetime = user_from_db.modified_at or user_from_db.created_at 
    context_string = f"{user_from_db.hash_password}{context_time.strftime('%d/%m/%Y,%H:%M:%S')}-verify" 
    
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

@auth_router.post("/login")
async def login_with_cookie(
    user: UserLoginData,
    response: Response,
    users: UsersServiceDependency,
    auth: AuthServiceDependency,
):
    user_from_db = users.get_one(username=user.username, with_password=True)
    if not user_from_db or not user_from_db["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist or inactive"
            )
    return auth.login_and_set_access_token(password=user.password, user_from_db=user_from_db, response=response)

@auth_router.get("/authenticated_user")
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

@auth_router.post("/refresh")
async def refresh_credentials(response: Response, auth: AuthServiceDependency, refresh: RefreshCredentials):
    return auth.refresh_access_token(response, refresh)
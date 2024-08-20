from fastapi import APIRouter, Response

from ..models import CreationUser, LoginUser
from ..services import UsersServiceDependency, AuthServiceDependency, SecurityDependency

auth_router = APIRouter(prefix="/auth", tags=["Auth"])




@auth_router.post("/register")
async def register(user: CreationUser, users: UsersServiceDependency, auth: AuthServiceDependency):
    hash_password = auth.get_password_hash(user.password)
    result = users.create_one(user, hash_password)
    return {"result message": f"User created with id: {result.inserted_id}"}


@auth_router.post("/login")
async def login_with_cookie(
    user: LoginUser,
    response: Response,
    users: UsersServiceDependency,
    auth: AuthServiceDependency,
):
    user_from_db = users.get_one(username=user.username, with_password=True)
    return auth.login_and_set_access_token(
        user=user, user_from_db=user_from_db, response=response
    )


@auth_router.get("/authenticated_user")
async def read_current_user(security: SecurityDependency):
    return dict(
        id=security.auth_user_id,
        name=security.auth_user_name,
        email=security.auth_user_email,
        role=security.auth_user_role,
    )

@auth_router.post("/refresh")
async def refresh_credentials(response: Response, auth: AuthServiceDependency):
    return auth.refresh_access_token(response)


    
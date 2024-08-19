from fastapi import APIRouter, Response

from ..models import CreationUser, LoginUser
from ..services import UsersServiceDependency, AuthCredentials

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

@auth_router.get("/")
async def list_users(users: UsersServiceDependency):
    return users.get_all()


@auth_router.post("/register")
async def register(user: CreationUser, auth: UsersServiceDependency):
    result = auth.create_one(user)
    return {"result message": f"User created with id: {result.inserted_id}"}


@auth_router.post("/login")
async def login_with_cookie(
    user: LoginUser,
    response: Response,
    auth: UsersServiceDependency,
):
    return auth.login_and_set_access_token(user, response)


@auth_router.get("/authenticated_user")
async def read_current_user(credentials: AuthCredentials):
    return credentials.subject

@auth_router.post("/refresh")
async def refresh_credentials(response: Response, credentials: AuthCredentials, auth: UsersServiceDependency):
    return auth.refresh_access_token(response, credentials)


    
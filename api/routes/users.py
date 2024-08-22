from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic_mongo import PydanticObjectId

from ..models import BaseUser, UserRegisterData, UserUpdateData
from ..services import UsersServiceDependency, AuthServiceDependency, SecurityDependency
from ..__common_deps import QueryParamsDependency

users_router = APIRouter(prefix="/Users", tags=["Users"])


@users_router.post("/")
def create_user(user: UserRegisterData, users: UsersServiceDependency, auth: AuthServiceDependency):
    hash_password = auth.get_password_hash(user.password)
    result = users.create_one(user, hash_password)
    return {"result message": f"User created with id: {result.inserted_id}"}


@users_router.get("/")
def get_all_users(users: UsersServiceDependency, params: QueryParamsDependency):
    return users.get_all(params)


@users_router.get("/{id}")
def get_one_user(id: PydanticObjectId, users: UsersServiceDependency):
    return users.get_one(id=id)


@users_router.put("/{id}")
def update_user(
    id: PydanticObjectId, user: UserUpdateData, users: UsersServiceDependency, security: SecurityDependency
):
    """
    Authenticated user only!
    """
    auth_user_id = security.auth_user_id
    assert (
        auth_user_id == str(id) or security.auth_user_role == "admin"
    ), "Access forbidden"
    return users.update_one(id=id, user=user)


@users_router.delete("/{id}")
def delete_user(id: PydanticObjectId, users: UsersServiceDependency, security: SecurityDependency):
    """
    Admins only!
    """
    security.is_admin_or_raise
    result = users.delete_one(id=id)
    if result:
        return {"result message": "User succesfully deleted",
                "deleted user": result}
    else:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"User with id: {id} was not found."},
                )

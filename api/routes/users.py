from fastapi import APIRouter, HTTPException, status
from pydantic_mongo import PydanticObjectId

from ..models import UserUpdateData, AdminRegisterData
from ..services import UsersServiceDependency, AuthServiceDependency, SecurityDependency
from ..__common_deps import QueryParamsDependency

users_router = APIRouter(prefix="/Users", tags=["Users"])

@users_router.get("/")
def get_all_users(users: UsersServiceDependency, params: QueryParamsDependency, security: SecurityDependency):
    """
    Admins only!
    """
    security.is_admin_or_raise
    return users.get_all(params)

@users_router.get("/{id}")
def get_one_user_by_id(id: PydanticObjectId, users: UsersServiceDependency, security: SecurityDependency):
    """
    Authenticated user only!
    """
    security.check_user_permission(str(id))
    if user := users.get_one(id=id):
        return user
    else:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} was not found."
            )

@users_router.post("/")
def create_user(user: AdminRegisterData, users: UsersServiceDependency, auth: AuthServiceDependency, security: SecurityDependency):
    """
    Admins only!
    """
    security.is_admin_or_raise
    hash_password = auth.get_password_hash(user.password)
    result = users.create_one(user, hash_password)
    return {"result message": f"User created with id: {result.inserted_id}"}

@users_router.put("/{id}")
def update_user(
    id: PydanticObjectId, user: UserUpdateData, users: UsersServiceDependency, security: SecurityDependency
):
    """
    Authenticated user only!
    """
    security.check_user_permission(str(id))
    return users.update_one(id=id, user=user)

@users_router.delete("/{id}")
def delete_user(id: PydanticObjectId, users: UsersServiceDependency, security: SecurityDependency):
    """
    Admins only!
    """
    security.is_admin_or_raise
    result = users.delete_one(id=id)
    return {"result message": "User succesfully deleted", "deleted user": result}


from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic_mongo import PydanticObjectId

from ..models import UserUpdateData, AdminRegisterData, AdminUpdateData
from ..services import UsersServiceDependency, AuthServiceDependency, SecurityDependency
from ..__common_deps import QueryParamsDependency

users_router = APIRouter(prefix="/Users", tags=["Users"])

@users_router.get("/")
async def get_all_users(users: UsersServiceDependency, params: QueryParamsDependency, security: SecurityDependency):
    """
    Admins only!
    """
    security.is_admin_or_raise
    return users.get_all(params)

@users_router.get("/{id}")
async def get_one_user_by_id(id: PydanticObjectId, users: UsersServiceDependency, security: SecurityDependency):
    """
    Authenticated user only!
    """
    security.check_user_permission(id)
    if user := users.get_one(id=id):
        return user.model_dump()
    else:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} was not found."
            )

@users_router.post("/")
async def create_user(
    user: AdminRegisterData,
    users: UsersServiceDependency,
    auth: AuthServiceDependency,
    security: SecurityDependency
):
    """
    Admins only!
    """
    security.is_admin_or_raise
    hash_password = auth.get_password_hash(user.password)
    result = users.create_one(user, hash_password)
    if result.acknowledged:
        return {"message": "New user succesfully created",
                "inserted_id": f"{result.inserted_id}"}
    else:
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": f"An unexpected error ocurred while creating order"},
            )

@users_router.put("/make_admin/{id}")
async def make_user_admin(
    id: PydanticObjectId,
    user: AdminUpdateData,
    users: UsersServiceDependency,
    security: SecurityDependency
):
    """
    Admins only!
    """
    security.is_admin_or_raise
    return users.update_one(id=id, user=user)

@users_router.put("/{id}")
async def update_user(
    id: PydanticObjectId,
    user: UserUpdateData,
    users: UsersServiceDependency,
    security: SecurityDependency
):
    """
    Authenticated user only!
    """
    security.check_user_permission(id)
    return users.update_one(id=id, user=user)

@users_router.delete("/{id}")
async def delete_user(id: PydanticObjectId, users: UsersServiceDependency, security: SecurityDependency):
    """
    Admins only!
    """
    security.is_admin_or_raise
    result = users.delete_one(id=id)
    return {"message": "User succesfully deleted", "deleted user": result}


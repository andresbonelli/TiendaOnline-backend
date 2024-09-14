__all__ = ["UsersServiceDependency", "UsersService"]


from fastapi import Depends, HTTPException, status
from pydantic import EmailStr
from pydantic_mongo import PydanticObjectId
from pydantic_core import ValidationError
from typing import Annotated
from datetime import datetime

from ..config import COLLECTIONS, db
from ..models import UserRegisterData, PrivateUserFromDB, UserFromDB, UserUpdateData
from ..__common_deps import QueryParamsDependency

class UsersService:
    assert (collection_name := "users") in COLLECTIONS
    collection = db[collection_name]

    @classmethod
    def get_all(cls, params: QueryParamsDependency):
        response_dict = {"users": [], "errors": []}
        results = params.query_collection(cls.collection)
        for user in results:
            try:
               response_dict["users"].append(
                   UserFromDB.model_validate(user).model_dump()
                   ) 
            except ValidationError as e:
                response_dict["errors"].append(f"Validation error: {e}")
        return response_dict

    @classmethod
    def get_one(
        cls,
        *,
        id: PydanticObjectId | None = None,
        username: str | None = None,
        email: EmailStr | None = None,
        with_password: bool = False,
    ):
        if all(q is None for q in (id, username, email)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No id, username or email provided",
            )
        filter = {
            "$or": [
                {"_id": id},
                {"username": username},
                {"email": email},
            ]
        }
        if user_from_db := cls.collection.find_one(filter):
            return (
                PrivateUserFromDB.model_validate(user_from_db)
                if with_password
                else UserFromDB.model_validate(user_from_db)
            )
        else:
            return None

    @classmethod
    def create_one(cls, user: UserRegisterData, hash_password: str, make_it_admin: bool = False):
        existing_user = cls.get_one(
            username=user.username,
            email=user.email,
        )  
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            )
        new_user = user.model_dump(exclude={"password"}, exclude_unset=True)
        new_user.update(
            hash_password=hash_password,
            created_at=datetime.now(),
            is_active=True if make_it_admin else False,
            role="admin" if make_it_admin else new_user["role"]
        )
        return cls.collection.insert_one(new_user) or None

    @classmethod
    def update_one(cls, id: PydanticObjectId, user: UserUpdateData):
        modified_user = user.model_dump(exclude={"password", "username", "email"}, exclude_unset=True)
        modified_user.update(modified_at=datetime.now())

        if document := cls.collection.find_one_and_update(
            {"_id": id},
            {"$set": modified_user},
            return_document=True,
        ):
            return UserFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} was not found."
            )
    
    @classmethod
    def update_password(cls, id: PydanticObjectId, hash_password: str):
        if document := cls.collection.find_one_and_update(
            {"_id": id},
            {"$set": {"hash_password": hash_password, "modified_at": datetime.now()}},
            return_document=True,
        ):
            return PrivateUserFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} was not found."
            )

    @classmethod
    def delete_one(cls, id: PydanticObjectId):
        document = cls.collection.find_one_and_delete({"_id": id})
        if document:
            return UserFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} was not found."
            )


UsersServiceDependency = Annotated[UsersService, Depends()]

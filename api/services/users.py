__all__ = ["UsersServiceDependency", "UsersService"]


from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId
from pydantic import EmailStr

from datetime import datetime

from ..config import COLLECTIONS, db
from ..models import CreationUser, PrivateUserFromDB, PublicUserFromDB, UpdationUser
from ..__common_deps import QueryParamsDependency


class UsersService:
    assert (collection_name := "users") in COLLECTIONS
    collection = db[collection_name]

    @classmethod
    def create_one(
        cls, user: CreationUser, hash_password: str, make_it_admin: bool = False
    ):
        try:
            existing_user = cls.get_one(
                username=user.username,
                email=user.email,
            )
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="User already exists"
                )
        except HTTPException:
            pass
        
        insert_user = user.model_dump(exclude={"password"}, exclude_unset=True)
        insert_user.update(hash_password=hash_password)
        insert_user.update(created_at=datetime.now())

        if make_it_admin:
            insert_user.update(role="admin")

        return cls.collection.insert_one(insert_user) or None
       

    @classmethod
    def get_all(cls, params: QueryParamsDependency):
        return [
            PublicUserFromDB.model_validate(user).model_dump()
            for user in params.query_collection(cls.collection)
        ]

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

        if db_user := cls.collection.find_one(filter):
            return (
                PrivateUserFromDB.model_validate(db_user).model_dump()
                if with_password
                else PublicUserFromDB.model_validate(db_user).model_dump()
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    @classmethod
    def update_one(cls, id: PydanticObjectId, user: UpdationUser):
        user.modified_at = datetime.now()
        print(user.model_dump())
        document = cls.collection.find_one_and_update(
            {"_id": id},
            {"$set": user.model_dump(exclude={"password"}, exclude_unset=True)},
            return_document=True,
        )

        if document:
            return PublicUserFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    @classmethod
    def update_password(cls, id: PydanticObjectId, hash_password: str):
        document = cls.collection.find_one_and_update(
            {"_id": id},
            {"$set": {"hash_password": hash_password, "modifiet_at": str(datetime.now())}},
            return_document=True,
        )
        if document:
            return PrivateUserFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    @classmethod
    def delete_one(cls, id: PydanticObjectId):
        document = cls.collection.find_one_and_delete({"_id": id})
        if document:
            return PublicUserFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )


UsersServiceDependency = Annotated[UsersService, Depends()]

__all__ = ["UsersServiceDependency", "AuthServiceDependency", "AuthCredentials"]


from typing import Annotated

from fastapi import Depends, HTTPException, Response, Security, status
from fastapi_jwt import JwtAccessBearerCookie, JwtAuthorizationCredentials, JwtRefreshBearer
from passlib.context import CryptContext
from pydantic_mongo import PydanticObjectId
from pydantic import EmailStr

from ..config import COLLECTIONS, db, access_token_exp, refresh_token_exp, SECRET_KEY, REFRESH_KEY
from ..models import CreationUser, LoginUser, UserFromDB, PublicUserFromDB, UserFromDBWithHash

access_security = JwtAccessBearerCookie(secret_key=SECRET_KEY, access_expires_delta=access_token_exp, auto_error=True)
refresh_security = JwtRefreshBearer(secret_key=REFRESH_KEY, auto_error=True)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


class UsersService:
    assert (collection_name := "users") in COLLECTIONS, f"Collection (table) {collection_name} does not exist in database"
    collection = db[collection_name]

    @classmethod
    def get_all(cls, role=None):
        filter = {"role": role} if role else {}
        return [
            UserFromDB.model_validate(user).model_dump()
            for user in cls.collection.find(filter)
            ]

    @classmethod
    def get_one(
        cls,
        id: PydanticObjectId | None = None,
        username: str | None = None,
        email: EmailStr | None = None,
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
            return UserFromDBWithHash.model_validate(user_from_db).model_dump()
        else:
            return None

    @classmethod
    def create_one(cls, user: CreationUser):
        existing_user = cls.get_one(
            username=user.username,
            email=user.email,
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            )

        insert_user = user.model_dump(exclude={"password"})
        insert_user.update(hash_password=get_password_hash(user.password))

        return cls.collection.insert_one(insert_user)

    @classmethod
    def login_and_set_access_token(cls, user: LoginUser, response: Response):

        existing_user = cls.get_one(username=user.username)
        if not existing_user or not verify_password(
            user.password, existing_user.get("hash_password")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        userdata: dict = PublicUserFromDB.model_validate(existing_user).model_dump()
        access_token = access_security.create_access_token(
            subject=userdata
        )
        refresh_token = refresh_security.create_refresh_token(
            subject=userdata, expires_delta=refresh_token_exp
        )
        access_security.set_access_cookie(response, access_token)
        refresh_security.set_refresh_cookie(response, refresh_token)

        return {"access_token": access_token, "refresh_token": refresh_token}
    
    @classmethod
    def refresh_access_token(cls, response: Response, refresh_credentials: JwtAuthorizationCredentials = Security(refresh_security)):
        access_token = access_security.create_access_token(subject=refresh_credentials.subject)
        refresh_token = refresh_security.create_refresh_token(subject=refresh_credentials.subject, expires_delta=refresh_token_exp)

        access_security.set_access_cookie(response, access_token)
        refresh_security.set_refresh_cookie(response, refresh_token)
        
        return {"access_token": access_token, "refresh_token": refresh_token}
        

UsersServiceDependency = Annotated[UsersService, Depends()]
AuthCredentials = Annotated[JwtAuthorizationCredentials, Security(access_security)]


class AuthService:
    def __init__(self, credentials: AuthCredentials):
        self.credentials = credentials
        self.role = self.credentials.subject.get("role")
        
    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_customer(self):
        return self.role == "customer"

    @property
    def is_staff(self):
        return self.role == "staff"


AuthServiceDependency = Annotated[AuthService, Depends()]
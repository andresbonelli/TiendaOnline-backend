__all__ = ["AuthServiceDependency", "SecurityDependency", "AuthService", "RefreshCredentials"]


from typing import Annotated

from fastapi import Depends, HTTPException, Response, Security, status
from fastapi_jwt import JwtAccessBearerCookie, JwtAuthorizationCredentials, JwtRefreshBearer
from fastapi.encoders import jsonable_encoder
from passlib.context import CryptContext


from ..config import access_token_exp, refresh_token_exp, SECRET_KEY, REFRESH_KEY
from ..models import UserLoginData,PublicUserFromDB

access_security = JwtAccessBearerCookie(secret_key=SECRET_KEY, access_expires_delta=access_token_exp, auto_error=True)
refresh_security = JwtRefreshBearer(secret_key=REFRESH_KEY, auto_error=True)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

AuthCredentials = Annotated[JwtAuthorizationCredentials, Security(access_security)]
RefreshCredentials = Annotated[JwtAuthorizationCredentials, Security(refresh_security)]






class AuthService:  
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    def login_and_set_access_token(
        self, user_from_db: dict | None, user: UserLoginData, response: Response
    ):
        if not user_from_db or not self.verify_password(
            user.password, user_from_db.get("hash_password")
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or credentials incorrect",
            )

        userdata = PublicUserFromDB.model_validate(user_from_db).model_dump()
        access_token = access_security.create_access_token(
            subject=jsonable_encoder(userdata), expires_delta=access_token_exp
        )
        refresh_token = refresh_security.create_refresh_token(
            subject=jsonable_encoder(userdata), expires_delta=refresh_token_exp
            )
        access_security.set_access_cookie(response, access_token)
        refresh_security.set_refresh_cookie(response, refresh_token)

        return {"access_token": access_token, "refresh_token": refresh_token}

    @classmethod
    def refresh_access_token(cls, response: Response, refresh: RefreshCredentials):
        access_token = access_security.create_access_token(subject=refresh.subject)
        refresh_token = refresh_security.create_refresh_token(subject=refresh.subject, expires_delta=refresh_token_exp)
  
        access_security.set_access_cookie(response, access_token)
        refresh_security.set_refresh_cookie(response, refresh_token)
  
        return {"access_token": access_token, "refresh_token": refresh_token}

class SecurityService:
    def __init__(self, credentials: AuthCredentials):
        self.auth_user_id = credentials.subject.get("id")
        self.auth_user_name = credentials.subject.get("username")
        self.auth_user_email = credentials.subject.get("email")
        self.auth_user_role = credentials.subject.get("role")  
        self.auth_user_created_at = credentials.subject.get("created_at")
        self.auth_user_modified_at = credentials.subject.get("modified_at")
        self.auth_user_address: list = credentials.subject.get("address")
        
    @property
    def is_admin(self):
        return self.auth_user_role == "admin"

    @property
    def is_staff(self):
        role = self.auth_user_role
        return role == "admin" or role == "staff"

    @property
    def is_customer(self):
        role = self.auth_user_role
        return role == "admin" or role == "customer"

    @property
    def is_admin_or_raise(self):
        assert self.auth_user_role == "admin", "User does not have admin role"

    @property
    def is_staff_or_raise(self):
        role = self.auth_user_role
        assert role == "admin" or role == "staff", "User does not have seller role"

    @property
    def is_customer_or_raise(self):
        role = self.auth_user_role
        assert role == "admin" or role == "customer", "User does not have customer role"

AuthServiceDependency = Annotated[AuthService, Depends()]
SecurityDependency = Annotated[SecurityService, Depends()]



    
        





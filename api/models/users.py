__all__ = [
    "BaseUser",
    "UserLoginData",
    "UserFromDB",
    "PrivateUserFromDB",
    "UserRegisterData",
    "AdminRegisterData",
    "UserUpdateData",
    "UserVerifyRequest",
    "UserResetPasswordRequest",
]

from pydantic import BaseModel, Field, EmailStr, AliasChoices
from pydantic_mongo import PydanticObjectId
from datetime import datetime
from enum import Enum

from ..config import CountryCode

class CreationRole(str, Enum):
    CUSTOMER = "customer"
    STAFF = "staff"

class Role(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    STAFF = "staff"

class Address(BaseModel):
    address_street_no: str | None = None
    address_street_name: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_country_code: CountryCode | None = None
    address_postal_code: str | None = None
    
class BaseUser(BaseModel):
    username: str
    role: Role = Field(default=Role.CUSTOMER)
    email: EmailStr
    firstname: str | None = None
    lastname: str | None = None
    image: str | None = None
    address: list[Address] | None = None   

class UserLoginData(BaseModel):
    input: str | EmailStr
    password: str
    
class UserVerifyRequest(BaseModel):
    token: str
    email: EmailStr

class UserResetPasswordRequest(UserVerifyRequest):
    new_password: str
    
class UserRegisterData(BaseUser):
    role: CreationRole = Field(default=CreationRole.CUSTOMER)
    password: str 

class AdminRegisterData(BaseUser):
    role: CreationRole = Field(default=CreationRole.STAFF)
    password: str 
    is_active: bool = Field(default=True)
    
class UserUpdateData(BaseUser):
    username: str = None
    role: CreationRole = Field(default=CreationRole.CUSTOMER)
    email: EmailStr = None
    image: str | None = None
    is_active: bool | None = None # Switch to Field(default=True) in production

class UserFromDB(BaseUser):
    id: PydanticObjectId = Field(validation_alias=AliasChoices("_id", "id"))
    is_active: bool | None = None # Switch to required in production
    created_at: datetime
    modified_at: datetime | None = None
    
class PrivateUserFromDB(UserFromDB):
    hash_password: str

   

  

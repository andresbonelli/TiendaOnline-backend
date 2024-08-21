
__all__ = [
    "BaseUser",
    "UserLoginData",
    "PublicUserFromDB",
    "PrivateUserFromDB",
    "UserRegisterData",
    "UserUpdateData",
]

from pydantic import BaseModel, Field, EmailStr, AliasChoices
from pydantic_mongo import PydanticObjectId
from typing import List, Optional
from datetime import datetime
from ..config import CountryCode
from enum import Enum

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
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    image: Optional[str] = None
    address: Optional[List[Address]] = None   

class UserUpdateData(BaseUser):
    username: str = None
    role: CreationRole = Field(default=CreationRole.CUSTOMER)
    email: EmailStr = None
    image: str | None = None

class UserRegisterData(BaseUser):
    role: CreationRole = Field(default=CreationRole.CUSTOMER)
    password: str 
    
class UserLoginData(BaseModel):
    username: str
    password: str

class PublicUserFromDB(BaseUser):
    id: PydanticObjectId = Field(validation_alias=AliasChoices("_id", "id"))
    created_at: datetime = None
    modified_at: datetime | None = None
    
class PrivateUserFromDB(BaseUser):
    id: PydanticObjectId = Field(alias="_id")
    hash_password: str
    created_at: datetime = None
    modified_at: Optional[datetime] = None
   

  

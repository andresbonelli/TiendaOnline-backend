
__all__ = [
    "BaseUser",
    "LoginUser",
    "PublicUserFromDB",
    "PrivateUserFromDB",
    "CreationUser",
    "UpdationUser",
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

class Adress(BaseModel):
    adress_street_no: Optional[str] = None
    adress_street_name: Optional[str] = None
    adress_city: Optional[str] = None
    adress_state: Optional[str] = None
    adress_country_code: Optional[CountryCode] = None
    adress_postal_code: Optional[str] = None
    
class BaseUser(BaseModel):
    username: str
    role: Role = Field(default=Role.CUSTOMER)
    email: EmailStr
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    image: Optional[str] = None
    address: Optional[List[Adress]] = None   

class UpdationUser(BaseUser):
    username: str = Field(default=None)
    role: Role = Field(default=None)
    email: EmailStr = Field(default=None)
    image: str | None = Field(default=None)
    modified_at: datetime = Field(default_factory=datetime.now)

class CreationUser(BaseUser):
    role: CreationRole = CreationRole.CUSTOMER
    password: str
    created_at: datetime = Field(default_factory=datetime.now)
    
class LoginUser(BaseModel):
    username: str
    password: str

class PublicUserFromDB(BaseUser):
    id: PydanticObjectId = Field(validation_alias=AliasChoices("_id", "id"))
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    
class PrivateUserFromDB(BaseUser):
    id: PydanticObjectId = Field(alias="_id")
    hash_password: str
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
   

  

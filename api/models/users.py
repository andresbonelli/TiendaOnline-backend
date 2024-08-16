
__all__ = [
    "BaseUser",
    "LoginUser",
    "UserFromDB",
    "UserFromDBWithHash",
    "CreationUser",
]

from pydantic import BaseModel, Field, EmailStr
from pydantic_mongo import PydanticObjectId
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    STAFF = "staff"

class Adress(BaseModel):
    adress_street_no: Optional[str] = None
    adress_street_name: Optional[str] = None
    adress_city: Optional[str] = None
    adress_state: Optional[str] = None
    adress_country_code: Optional[str] = None #Enum?
    adress_postal_code: Optional[str] = None
    
class BaseUser(BaseModel):
    username: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    role: Role = Field(default=Role.ADMIN)
    email: EmailStr
    image: Optional[str] = None
    address: Optional[List[Adress]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
    
    
class LoginUser(BaseModel):
    username: str
    password: str

class CreationUser(BaseUser):
    password: str
    
class UserFromDB(BaseUser):
    id: PydanticObjectId
   
class UserFromDBWithHash(BaseUser):
    id: PydanticObjectId = Field(alias="_id")
    hash_password: str
  

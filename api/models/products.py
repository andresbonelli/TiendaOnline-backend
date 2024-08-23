__all__ = [
    "BaseProduct",
    "ProductCreateData",
    "ProductUpdateData",
    "ProductFromDB"
    ]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Details(BaseModel):
    pass
    # TODO: add custom details

class BaseProduct(BaseModel):
    name: str
    description: str
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    sku: str | None = None
    image: str | None = None
    category: str | None = None  #Enum
    details: Details | None = None
    tags: List[str] | None = None


class ProductCreateData(BaseProduct):
    staff_id: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.now)

    
class ProductUpdateData(BaseProduct):
    staff_id: PydanticObjectId | None = None
    name: str | None = None
    description: str | None = None
    price: float | None = Field(ge=0, default=None)
    stock: int | None = Field(ge=0, default=None)
    sales_count: int | None = Field(ge=0, default=None)
    modified_at: datetime = Field(default_factory=datetime.now)

  
class ProductFromDB(BaseProduct):
    id: PydanticObjectId = Field(alias="_id")
    staff_id: PydanticObjectId | None = None
    modified_at: datetime | None = None
    created_at: datetime
    
class PrivateProductFromDB(BaseProduct):
    pass
    
    

    

    
    
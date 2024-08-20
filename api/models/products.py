__all__ = ["Product", "ProductFromDB", "UpdationProduct"]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Details(BaseModel):
    pass
    # TODO: add custom details

class Product(BaseModel):
    staff_id: PydanticObjectId
    name: str
    description: str
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    sku: Optional[str] = None
    image: str = Field(default=None)
    sales_count: Optional[int] = Field(ge=0, default=None)
    category: Optional[str] = None  #Enum
    details: Optional[Details] = None
    tags: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.now)

class UpdationProduct(BaseModel):
    staff_id: PydanticObjectId = Field(default=None)
    name: str = Field(default=None)
    description: str = Field(default=None)
    price: float = Field(ge=0, default=None)
    stock: int = Field(ge=0, default=None)
    image: str = Field(default=None)
    #created_at: datetime = Field(default=None)
    modified_at: datetime = Field(default=None)

  
class ProductFromDB(Product):
    id: PydanticObjectId = Field(alias="_id")
    modified_at: datetime = Field(default=None)
    

    
    

    

    
    
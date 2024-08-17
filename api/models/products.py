__all__ = ["Product", "ProductFromDB", "UpdateProductData"]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import List, Optional
from datetime import datetime
from enum import Enum


class Details(BaseModel):
    pass
    # TODO: add custom details

class Product(BaseModel):
    name: str
    description: str
    price: float = Field(ge=0)
    stock: int = Field(ge=0)
    sku: Optional[str] = None
    sales_count: Optional[int] = Field(ge=0, default=None)
    category: Optional[str] = None  #Enum
    details: Optional[Details] = None
    tags: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    # class Config:
    #     json_encoders = {
    #         datetime: lambda dt: dt.isoformat(),
    #     }
    
class ProductFromDB(Product):
    id: PydanticObjectId = Field(alias="_id")
    modified_at: Optional[datetime] = None
    
class UpdateProductData(Product):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(ge=0, default=None)
    stock: Optional[int] = Field(ge=0, default=None)
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    
    

    

    
    
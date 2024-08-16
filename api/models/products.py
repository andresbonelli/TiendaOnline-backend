__all__ = ["Product", "ProductFromDB"]

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
    sales_count: int | None = Field(ge=0, default=None)
    category: Optional[str] = None  #Enum
    details: Optional[Details] = None
    tags: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
    

    
class ProductFromDB(Product):
    id: PydanticObjectId = Field(alias="_id")
    

    
    
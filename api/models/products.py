__all__ = [
    "BaseProduct",
    "ProductCreateData",
    "ProductUpdateData",
    "ProductFromDB",
    "DeletedProductFromDB"
    ]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from datetime import datetime
from ..config.constants import Size, Category


class ProductDetails(BaseModel):
    image_list: list[str] | None = None
    sizes: list[Size] | None = None
    long_description: str | None = None

class BaseProduct(BaseModel):
    name: str
    description: str
    price: float = Field(ge=0)
    old_price: float | None = None
    stock: int = Field(ge=0)
    sku: str | None = None
    image: str | None = None
    category: Category | None = None 
    details: ProductDetails | None = None
    tags: list[str] | None = None

class ProductCreateData(BaseProduct):
    staff_id: PydanticObjectId
    created_at: datetime = Field(default_factory=datetime.now)
    
class ProductUpdateData(BaseProduct):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(ge=0, default=None)
    stock: int | None = Field(ge=0, default=None)
    sales_count: int | None = Field(ge=0, default=None)

class ProductFromDB(BaseProduct):
    id: PydanticObjectId = Field(alias="_id")
    staff_id: PydanticObjectId
    sales_count: int | None = None
    created_at: datetime
    modified_at: datetime | None = None
    
class DeletedProductFromDB(ProductFromDB):
    deleted_at: datetime
    
    
    

    

    
    
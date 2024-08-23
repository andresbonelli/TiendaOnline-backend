__all__ = ["BaseOrder", "OrderFromDB", "OrderCreateData", "OrderUpdateData", "PrivateOrderFromDB"]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from datetime import datetime


class BaseOrder(BaseModel):
    product_id: PydanticObjectId
    quantity: int
    
class OrderCreateData(BaseOrder):
    customer_id: PydanticObjectId
    total_price: float
    created_at: datetime = Field(default_factory=datetime.now)
    
class OrderUpdateData(BaseOrder):
    customer_id: PydanticObjectId | None = None
    product_id: PydanticObjectId | None = None
    modified_at: datetime = Field(default_factory=datetime.now)

class OrderFromDB(BaseOrder):
    id: PydanticObjectId = Field(alias="_id")
    customer_id: PydanticObjectId
    created_at: datetime
    modified_at: datetime | None = None
    
class PrivateOrderFromDB(BaseOrder):
    pass

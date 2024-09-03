__all__ = ["BaseOrder", "OrderFromDB", "OrderCreateData", "OrderUpdateData", "OrderStatus"]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from datetime import datetime
from enum import Enum 


class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"
    
class OrderProduct(BaseModel):
    product_id: PydanticObjectId
    quantity: int

class BaseOrder(BaseModel):
    products: list[OrderProduct]
    
class OrderCreateData(BaseOrder):
    customer_id: PydanticObjectId
    status: OrderStatus = OrderStatus.pending
    created_at: datetime = Field(default_factory=datetime.now)
    
class OrderUpdateData(BaseOrder):   
    customer_id: PydanticObjectId | None = None
    products: list[OrderProduct] | None = None
    total_price: float | None = None
    status: OrderStatus = OrderStatus.pending

class OrderFromDB(BaseOrder):
    id: PydanticObjectId = Field(alias="_id")
    customer_id: PydanticObjectId
    created_at: datetime
    total_price: float | None = None
    status: OrderStatus
    modified_at: datetime | None = None
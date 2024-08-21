__all__ = ["BaseOrder", "OrderFromDB"]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class BaseOrder(BaseModel):
    customer_id: PydanticObjectId
    product_id: PydanticObjectId
    price: float
    quantity: int
    
class OrderCreateData(BaseOrder):
    pass

class OrderUpdateData(BaseOrder):
    pass

class OrderFromDB(BaseOrder):
    id: PydanticObjectId = Field(alias="_id")
    
class PrivateOrderFromDB(BaseOrder):
    pass

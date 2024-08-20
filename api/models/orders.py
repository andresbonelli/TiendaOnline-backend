__all__ = ["Order", "OrderFromDB"]

from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId


class Order(BaseModel):
    customer_id: PydanticObjectId
    product_id: PydanticObjectId
    price: float
    quantity: int


class OrderFromDB(Order):
    id: PydanticObjectId = Field(alias="_id")

__all__ = ["OrdersServiceDependency", "OrdersService"]

from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId

from ..__common_deps import QueryParamsDependency
from ..config import COLLECTIONS, db
from ..models import BaseOrder, OrderCreateData, OrderFromDB


class OrdersService:
    assert (collection_name := "orders") in COLLECTIONS
    collection = db[collection_name]

    @classmethod
    def get_all(cls, params: QueryParamsDependency):
        return [
            OrderFromDB.model_validate(order).model_dump()
            for order in params.query_collection(cls.collection)
        ]

    @classmethod
    def get_one(cls, id: PydanticObjectId, authorized_user_id: PydanticObjectId | None):
        filter_criteria: dict = {"_id": id}
        # WARNING: Filter criteria is always "order" id !!! 
        if authorized_user_id:
            filter_criteria.update(
                {
                    "$or": [
                        {"customer_id": authorized_user_id},
                        {"staff_id": authorized_user_id},
                    ]
                }
            )

        if order_from_db := cls.collection.find_one(filter_criteria):
            return OrderFromDB.model_validate(order_from_db).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

    @classmethod
    def create_one(cls, order: dict):
        OrderCreateData.model_validate(order)
        return cls.collection.insert_one(order) or None
 
    @classmethod
    def find_from_staff_id(cls, staff_id: PydanticObjectId):  
        lookup = {"$lookup": {
            "from": "products", "as": "products_result", "localField": "product_id", "foreignField": "_id" 
        }}
        unwind = {"$unwind": "$products_result"}
        matches = {"$match": {"products_result.staff_id": staff_id}}
        filtered_data = list(cls.collection.aggregate([lookup, unwind, matches]))
   
        return [OrderFromDB.model_validate(order).model_dump() for order in filtered_data]


OrdersServiceDependency = Annotated[OrdersService, Depends()]

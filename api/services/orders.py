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
    def create_one(cls, order: OrderCreateData):
        return cls.collection.insert_one(order.model_dump()) or None


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


OrdersServiceDependency = Annotated[OrdersService, Depends()]

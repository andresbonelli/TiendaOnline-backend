__all__ = ["OrdersServiceDependency", "OrdersService"]

from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId
from datetime import datetime

from ..__common_deps import QueryParamsDependency
from ..config import COLLECTIONS, db
from ..models import OrderUpdateData, OrderCreateData, OrderFromDB


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
    def get_one(cls, id: PydanticObjectId, authorized_user_id: PydanticObjectId | None=None):
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
        """
        WARNING: Method deprecated.
        """ 
        # TODO: Modify aggregation to search within array of products.
        lookup = {"$lookup": {
            "from": "products", "as": "products_result", "localField": "product_id", "foreignField": "_id" 
        }}
        unwind = {"$unwind": "$products_result"}
        matches = {"$match": {"products_result.staff_id": staff_id}}
        filtered_data = list(cls.collection.aggregate([lookup, unwind, matches]))
   
        return [OrderFromDB.model_validate(order).model_dump() for order in filtered_data]

    @classmethod
    def update_one(cls, order_id: PydanticObjectId, order: OrderUpdateData):
        modified_order: dict = order.model_dump(exclude_unset=True, exclude_none=True)
        modified_order.update(modified_at=datetime.now()) 
    
        document = cls.collection.find_one_and_update(
                {"_id": order_id},
                {"$set": modified_order},
                return_document=True,
            )

        if document:
            return OrderFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while updating order"
            )
    
    @classmethod
    def calculate_total_price(cls, order_id: PydanticObjectId):
        match = {"$match": {"_id": order_id}}
        unwind = {"$unwind": "$products"}
        lookup = {"$lookup": {
            "from": "products","localField": "products.product_id","foreignField": "_id","as": "productDetails"
            }}
        prod_unwind = {"$unwind": "$productDetails"}
        set = {"$set": {
            "productTotal": {
            "$multiply": ["$products.quantity", "$productDetails.price"]
            }}}
        group = {"$group": {
            "_id": "$_id",
            "totalPrice": {
            "$sum": "$productTotal"
            }}}
        
        
        cursor = cls.collection.aggregate([match,unwind,lookup,prod_unwind,set,group])
        return [doc["totalPrice"] for doc in cursor]

    
OrdersServiceDependency = Annotated[OrdersService, Depends()]

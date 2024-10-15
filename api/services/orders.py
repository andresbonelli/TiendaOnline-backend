__all__ = ["OrdersServiceDependency", "OrdersService"]

from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId
from pydantic_core import ValidationError
from typing import Annotated
from datetime import datetime

from ..__common_deps import QueryParamsDependency
from ..services import ProductsServiceDependency, UsersServiceDependency
from ..config import COLLECTIONS, db
from ..models import BaseOrder, OrderStatus, OrderFromDB, OrderUpdateData, CompletedOrderProduct

class OrdersService:
    assert (collection_name := "orders") in COLLECTIONS
    collection = db[collection_name]

    @classmethod
    def get_all(cls, params: QueryParamsDependency):
        response_dict = {"orders": [], "errors": []}
        results = params.query_collection(cls.collection)
        for order in results:
            try:
               response_dict["orders"].append(
                   OrderFromDB.model_validate(order).model_dump()
                   ) 
            except ValidationError as e:
                response_dict["errors"].append(f"Validation error: {e}")
        return response_dict

    @classmethod
    def get_one(cls, id: PydanticObjectId):
        if order_from_db := cls.collection.find_one({"_id": id}):
            try:
                return OrderFromDB.model_validate(order_from_db)
            except ValidationError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Validation error while fetching order: {e}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {id} not found"
            )
    
    @classmethod
    def find_from_customer_id(cls, id: PydanticObjectId):
        cursor = cls.collection.find({"customer_id": id})
        return [OrderFromDB.model_validate(order) for order in cursor]
         
    @classmethod
    def find_from_product_id(cls, id: PydanticObjectId):
        cursor = cls.collection.find({"products.product_id": id})
        return [OrderFromDB.model_validate(order) for order in cursor]
       
    @classmethod
    def find_from_staff_id(cls, staff_id: PydanticObjectId): 
        lookup = {"$lookup": {
            "from": "products", "as": "products_result", "localField": "products.product_id", "foreignField": "_id" 
        }}
        matches = {"$match": {"products_result.staff_id": staff_id}}
        cursor = cls.collection.aggregate([lookup, matches])
        return [OrderFromDB.model_validate(order).model_dump() for order in cursor]
    
    @classmethod
    def create_one(cls, order: BaseOrder, customer_id: PydanticObjectId, products: ProductsServiceDependency):
        products.check_stock(order.products)
        new_order: dict = {
        "customer_id": PydanticObjectId(customer_id),
        "products": [
                {
                "product_id": PydanticObjectId(product.product_id),
                "quantity": product.quantity
                }
                for product in order.products
            ],
        "status": OrderStatus.pending,
        "created_at": datetime.now()
    }
        return cls.collection.insert_one(new_order)

    @classmethod
    def update_one(cls, order_id: PydanticObjectId, order: OrderUpdateData):
        modified_order: dict = order.model_dump(exclude_unset=True, exclude_none=True)
        modified_order.update(modified_at=datetime.now()) 
        if document := cls.collection.find_one_and_update(
                {"_id": order_id},
                {"$set": modified_order},
                return_document=True,
            ):
            return OrderFromDB.model_validate(document)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected error while updating order"
            )
    
    @classmethod
    def calculate_total_price(cls, order_id: PydanticObjectId) -> list:
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
    
    @classmethod
    def get_order_products_with_details(cls, order_id: PydanticObjectId) -> list:
        match = {"$match": {"_id": order_id}}
        unwind = {"$unwind": "$products"}
        lookup = {
            "$lookup": {
                "from": "products",
                "localField": "products.product_id",
                "foreignField": "_id",
                "as": "productDetails"
            }
        }
        prod_unwind = {"$unwind": "$productDetails"}
        project = {
            "$project": {
                "_id": 0,
                "product_id": "$products.product_id",
                "quantity": "$products.quantity",
                "name": "$productDetails.name",
                "price": "$productDetails.price",
                "image": "$productDetails.image"
            }
        }
        cursor = cls.collection.aggregate([match, unwind, lookup, prod_unwind, project])
        return [CompletedOrderProduct.model_validate(doc) for doc in cursor]
    
    
OrdersServiceDependency = Annotated[OrdersService, Depends()]

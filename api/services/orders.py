__all__ = ["OrdersServiceDependency", "OrdersService"]

from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId
from pydantic_core import ValidationError
from typing import Annotated
from datetime import datetime

from ..__common_deps import QueryParamsDependency
from ..services import ProductsServiceDependency
from ..config import COLLECTIONS, db
from ..models import (
    BaseOrder,
    OrderStatus,
    OrderFromDB,
    OrderUpdateData,
    CompletedOrderProduct,
)


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
                    detail=f"Error de validación de orden: {e}",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden {id} no encontrada.",
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
        lookup = {
            "$lookup": {
                "from": "products",
                "as": "products_info",
                "localField": "products.product_id",
                "foreignField": "_id",
            }
        }
        matches = {"$match": {"products_info.staff_id": staff_id}}
        # Filtering only matching staff member products:
        projection = {
            "$project": {
                "products": {
                    #  Constructs the products list in the order, containing only the product_id
                    #  and corresponding quantity for matching products.
                    "$map": {
                        "input": {
                            # Filters the products_info list to include only products with the specified staff_id
                            "$filter": {
                                "input": "$products_info",
                                "as": "product",
                                "cond": {"$eq": ["$$product.staff_id", staff_id]},
                            }
                        },
                        "as": "filtered_product",
                        "in": {
                            "product_id": "$$filtered_product._id",
                            # Used to find the correct quantity for each filtered product based on its product_id.
                            "quantity": {
                                "$arrayElemAt": [
                                    "$products.quantity",
                                    {
                                        "$indexOfArray": [
                                            "$products.product_id",
                                            "$$filtered_product._id",
                                        ]
                                    },
                                ]
                            },
                        },
                    }
                },
                "id": 1,
                "customer_id": 1,
                "created_at": 1,
                "total_price": 1,
                "status": 1,
                "modified_at": 1,
            }
        }
        cursor = cls.collection.aggregate([lookup, matches, projection])
        return [OrderFromDB.model_validate(order).model_dump() for order in cursor]

    @classmethod
    def create_one(
        cls,
        order: BaseOrder,
        customer_id: PydanticObjectId,
        products: ProductsServiceDependency,
    ):
        products.check_stock(order.products)
        new_order: dict = {
            "customer_id": PydanticObjectId(customer_id),
            "products": [
                {
                    "product_id": PydanticObjectId(product.product_id),
                    "quantity": product.quantity,
                }
                for product in order.products
            ],
            "status": OrderStatus.pending,
            "created_at": datetime.now(),
        }
        return cls.collection.insert_one(new_order)

    @classmethod
    def update_one(cls, order_id: PydanticObjectId, order: OrderUpdateData):
        modified_order: dict = order.model_dump(exclude_unset=True, exclude_none=True)
        modified_order.update(
            products=[
                {
                    "product_id": PydanticObjectId(product.product_id),
                    "name": product.name,
                    "price": product.price,
                    "image": product.image,
                    "quantity": product.quantity,
                }
                for product in order.products
            ],
            modified_at=datetime.now(),
        )
        if document := cls.collection.find_one_and_update(
            {"_id": order_id},
            {"$set": modified_order},
            return_document=True,
        ):
            return OrderFromDB.model_validate(document)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error inesperado actualizando orden.",
            )

    @classmethod
    def calculate_total_price(cls, order_id: PydanticObjectId) -> list:
        match = {"$match": {"_id": order_id}}
        unwind = {"$unwind": "$products"}
        lookup = {
            "$lookup": {
                "from": "products",
                "localField": "products.product_id",
                "foreignField": "_id",
                "as": "productDetails",
            }
        }
        prod_unwind = {"$unwind": "$productDetails"}
        set = {
            "$set": {
                "productTotal": {
                    "$multiply": ["$products.quantity", "$productDetails.price"]
                }
            }
        }
        group = {"$group": {"_id": "$_id", "totalPrice": {"$sum": "$productTotal"}}}
        cursor = cls.collection.aggregate(
            [match, unwind, lookup, prod_unwind, set, group]
        )
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
                "as": "productDetails",
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
                "image": "$productDetails.image",
            }
        }
        cursor = cls.collection.aggregate([match, unwind, lookup, prod_unwind, project])
        return [CompletedOrderProduct.model_validate(doc) for doc in cursor]


OrdersServiceDependency = Annotated[OrdersService, Depends()]

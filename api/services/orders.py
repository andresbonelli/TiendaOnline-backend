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
    def create_one(cls, order: dict):
        OrderCreateData.model_validate(order)
        return cls.collection.insert_one(order) or None

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
    def create_one(cls, order: OrderCreateData):
        return cls.collection.insert_one(order.model_dump()) or None
    
    @classmethod
    def find_from_staff_id(cls, staff_id: PydanticObjectId):
        orders = cls.collection.aggregate([
        # primero tenemos que agregarle un campo a la colección orders
        # porque el product_id es de tipo "string", y el _id del producto posta es de tipo "ObjectId"
        # asi que lo convertimos y lo agregamos... este paso se podría simplificar si guardaramos las referencias
        # en ObjectId como se debe...

        {"$addFields": {"product_obj_id": {"$toObjectId": "$product_id"}}},
        # "product_obj_id" es nuestro nuevo campo

        # ahora hacemos lo que en una base de datos relacional sería como un "join"
        # es decir, vamos a unir la colección de "orders" con la de "products"
        # ahora que tenemos un campo de comparación lo podemos hacer

        {"$lookup": {"from": "products", "as": "joint_products", "localField": "product_obj_id", "foreignField": "_id"}},
        # en este punto las orders tendrian el nuevo campo "product_obj_id" y otro de tipo array "joint_products"
        # que dberia contener todos los products que tienen el id igual a "product_obj_id"... como es un campo único,
        # va a ser un array de un solo products

        # ahora necesitamos "desenrollar ese array" eso significa que por cada elemento del array vamos a tener una order,
        # con un único product... como hay uno solo, vamos a tener la misma cantidad de orders, pero "joint_product" ya no
        # va a ser un array, sino que va a tener un único objeto "product"
        {"$unwind": "$joint_products"},

        # ahora finalmente podemos filtrar las "orders" por el "seller_id" que está en "joint_product"
        {"$match": {"joint_product.seller_id": staff_id}},

        # por último podrían agregar un $project acá, para elejir que campos devolver a python... yo voy a filtrar
        # los que creé
        {"$project": {"joint_product": 0, "product_obj_id": 0}}
        ])
        return [
            OrderFromDB.model_validate(order).model_dump()
            for order in orders
        ]


OrdersServiceDependency = Annotated[OrdersService, Depends()]

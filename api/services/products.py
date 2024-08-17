__all__ = ["ProductsServiceDependency"]

from typing import Annotated, List

from fastapi import Depends, HTTPException, status, Query
from pydantic_mongo import PydanticObjectId
from datetime import datetime


from ..config import COLLECTIONS, db
from ..models import Product, ProductFromDB, UpdateProductData


class ProductsService:
    """
    This contains actual Mongo database CRUD methods.
    
    Will be injected as dependency in the API Routes.
    
    """
    assert (collection_name := "products") in COLLECTIONS, f"Collection (table) {collection_name} does not exist in database"
    collection = db[collection_name] 
    
    @classmethod
    def get_all(cls):
        return [
            ProductFromDB.model_validate(product).model_dump()
            for product in cls.collection.find()
            ]
        
    
    @classmethod
    def get_one(cls, id: PydanticObjectId):
        if product_from_db := cls.collection.find_one({"_id": id}):
            return ProductFromDB.model_validate(product_from_db).model_dump()
        else:
            return None
    
    @classmethod
    def create_one(cls, product: Product):
        return cls.collection.insert_one(product.model_dump())
        
    @classmethod
    def update_one(cls, id: PydanticObjectId, product_data: UpdateProductData):
        
        product_data.modified_at = datetime.now()
        return cls.collection.find_one_and_update(
            {"_id": id},
            {"$set": product_data.model_dump(exclude_unset=True)},
            return_document=True
        )
    
    @classmethod
    def delete_one(cls, id: PydanticObjectId):
        return cls.collection.find_one_and_delete({"_id": id})
    
    @classmethod
    def delete_many(cls, q: Query):
        return cls.collection.delete_many(q)


ProductsServiceDependency = Annotated[ProductsService, Depends()]
# Same as:
# ProductsServiceDependency = Annotated[ProductsService, Depends(ProductsService)]



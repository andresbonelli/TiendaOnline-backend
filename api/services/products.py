__all__ = ["ProductsServiceDependency", "ProductsService"]

from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId

from ..config import COLLECTIONS, db
from ..models import ProductCreateData, ProductUpdateData, ProductFromDB 
from ..__common_deps import QueryParamsDependency, SearchEngineDependency


class ProductsService:
    """
    This contains actual Mongo database CRUD methods.
    
    Will be injected as dependency in the API Routes.
    
    """
    assert (collection_name := "products") in COLLECTIONS, f"Collection (table) {collection_name} does not exist in database"
    collection = db[collection_name] 
    
    
    
    @classmethod
    def get_all(cls, params: QueryParamsDependency):
        return [
            ProductFromDB.model_validate(product).model_dump()
            for product in params.query_collection(cls.collection)
            ]
        
    @classmethod
    def search(cls, search: SearchEngineDependency):
        return [
            ProductFromDB.model_validate(product).model_dump()
            for product in search.atlas_search(cls.collection)
            ]
    
    @classmethod
    def autocomplete(cls, search: SearchEngineDependency):
        return search.autocomplete(cls.collection)
        
        
    @classmethod
    def get_one(cls, id: PydanticObjectId):
        if product_from_db := cls.collection.find_one({"_id": id}):
            return ProductFromDB.model_validate(product_from_db).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )
        
    @classmethod
    def create_one(cls, product: dict):
        ProductCreateData.model_validate(product)
        return cls.collection.insert_one(product) or None
    
    @classmethod
    def update_one(cls, id: PydanticObjectId, product: ProductUpdateData):
        # TODO: modify logic to check user id matches existing product staff_id 
        document = cls.collection.find_one_and_update(
            {"_id": id},
            {"$set": product.model_dump(exclude_unset=True)},
            return_document=True,
        )

        if document:
            return ProductFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

    @classmethod
    def delete_one(cls, id: PydanticObjectId):
        document = cls.collection.find_one_and_delete({"_id": id})
        if document:
            return ProductFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )


ProductsServiceDependency = Annotated[ProductsService, Depends()]        
# Same as:
# ProductsServiceDependency = Annotated[ProductsService, Depends(ProductsService)]



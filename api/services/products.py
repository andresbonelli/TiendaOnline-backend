__all__ = ["ProductsServiceDependency", "ProductsService"]

from fastapi import Depends, HTTPException, status
from pydantic_mongo import PydanticObjectId
from pydantic_core import ValidationError
from typing import Annotated
from datetime import datetime

from ..config import COLLECTIONS, db
from ..models import BaseProduct, ProductCreateData, ProductUpdateData, ProductFromDB, OrderProduct
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
        response_dict = {"product_list": [], "errors": []}
        results = params.query_collection(cls.collection)
        for product in results:
            try:
               response_dict["product_list"].append(
                   ProductFromDB.model_validate(product).model_dump()
                   ) 
            except ValidationError as e:
                response_dict["errors"].append(f"Validation error: {e}")      
        return response_dict
        
    @classmethod
    def search(cls, search: SearchEngineDependency):
        response_dict = {"product_list": [], "errors": []}
        results = search.atlas_search(cls.collection)
        for product in results:
            try:
               response_dict["product_list"].append(
                   ProductFromDB.model_validate(product).model_dump()
                   ) 
            except ValidationError as e:
                response_dict["errors"].append(f"Validation error: {e}")    
        return response_dict
    
    @classmethod
    def autocomplete(cls, search: SearchEngineDependency):
        return search.autocomplete(cls.collection)
            
    @classmethod
    def get_one(cls, id: PydanticObjectId):
        if product_from_db := cls.collection.find_one({"_id": id}):
            try:
                return ProductFromDB.model_validate(product_from_db)
            except ValidationError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Validation error while fetching product: {e}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {id} not found"
            )
        
    @classmethod
    def find_from_staff_id(cls, staff_id: PydanticObjectId): 
        cursor = cursor = cls.collection.find({"staff_id": staff_id})
        return [ProductFromDB.model_validate(product).model_dump() for product in cursor]
        
    @classmethod
    def create_one(cls, product: BaseProduct, staff_id: PydanticObjectId):
        # Check if product already exist in database. 
        if product.sku and cls.collection.find_one({"sku": product.sku}):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product already exists"
            )   
        new_product: dict = {
            **product.model_dump(),
            "staff_id": staff_id,
            "created_at":datetime.now()
        }
        ProductCreateData.model_validate(new_product)
        return cls.collection.insert_one(new_product) or None
    
    @classmethod
    def update_one(cls, id: PydanticObjectId, product: ProductUpdateData):  
        modified_product: dict = product.model_dump(exclude_unset=True)
        modified_product.update(modified_at=datetime.now())

        if document := cls.collection.find_one_and_update(
            {"_id": id},
            {"$set": modified_product},
            return_document=True,
        ):
            return ProductFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {id} not found"
            )

    @classmethod
    def delete_one(cls, id: PydanticObjectId):
        if document := cls.collection.find_one_and_delete({"_id": id}):
            return ProductFromDB.model_validate(document).model_dump()
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {id} not found"
            )
                
    @classmethod
    def check_stock(cls, order_products: list[OrderProduct]) -> None:
        for product in order_products:
            existing_product = cls.get_one(product.product_id)
            if existing_product.stock < product.quantity:
                raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Product {product.product_id} is out of stock"
                    )
    
    @classmethod
    def check_and_update_stock(cls, order_products: list[OrderProduct]) -> None:
        for product in order_products:
            existing_product = cls.get_one(product.product_id)
            if existing_product.stock < product.quantity:
                raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Product {product.product_id} is out of stock"
                    )
            product_to_update = ProductUpdateData(
                stock=existing_product.stock - product.quantity,
                sales_count=
                    existing_product.sales_count + product.quantity 
                    if existing_product.sales_count 
                    else product.quantity,
                modified_at=datetime.now()
                )
            cls.update_one(
                product.product_id,
                product_to_update,
            )

ProductsServiceDependency = Annotated[ProductsService, Depends()]        




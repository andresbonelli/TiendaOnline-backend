__all__ = ["products_router"]

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic_mongo import PydanticObjectId
from datetime import datetime

from ..models import BaseProduct, ProductCreateData, ProductUpdateData
from ..services import ProductsServiceDependency, SecurityDependency
from ..__common_deps import QueryParamsDependency

products_router = APIRouter(prefix="/products", tags=["Products"])


@products_router.get("/")
async def list_products(products: ProductsServiceDependency, params: QueryParamsDependency):
    return products.get_all(params)


@products_router.get("/{id}")
async def get_product(id: PydanticObjectId, products: ProductsServiceDependency):
    return products.get_one(id) or JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Product with id: {id} was not found."},
        )

@products_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(product: BaseProduct, products:  ProductsServiceDependency, security: SecurityDependency):
    """
    Staff members and admins only!
    """
    # Check current authenticated user is staff or admin
    security.is_staff_or_raise
    # Unpack values from base product Form and enforce staff ID and creation date
    new_product = ProductCreateData(**product.model_dump())
    new_product.staff_id = security.auth_user_id
    new_product.created_at = datetime.now()
    result = products.create_one(new_product)
    if result.acknowledged:
        return {"result message": f"Product created with id: {result.inserted_id}"}
    else:
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": f"An unexpected error ocurred while creating product"},
            )

@products_router.put("/{id}")
async def update_product(
    id: PydanticObjectId,
    product_data: BaseProduct,
    products: ProductsServiceDependency,
    security: SecurityDependency
    ):
    """
    Staff members and admins only!
    """
    security.is_staff_or_raise
    modified_product = ProductUpdateData(**product_data.model_dump())
    modified_product.modified_at = datetime.now()
    result = products.update_one(id, modified_product) 
    if result:
        return {"result message": "Product succesfully updated",
                "updated product": result}
    else:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"Product with id: {id} was not found."},
            )
  
    
@products_router.delete("/{id}")
async def delete_product(id: PydanticObjectId, products: ProductsServiceDependency, security: SecurityDependency):
    """
    Admins only!
    """
    security.is_admin_or_raise
    result = products.delete_one(id)
    if result:
        return {"result message": "Product succesfully deleted",
                "deleted product": result}
    else:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"Product with id: {id} was not found."},
                )

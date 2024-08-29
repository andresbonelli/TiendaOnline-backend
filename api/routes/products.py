__all__ = ["products_router"]

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic_mongo import PydanticObjectId


from ..models import BaseProduct, ProductUpdateData
from ..services import ProductsServiceDependency, SecurityDependency
from ..__common_deps import QueryParamsDependency, SearchEngineDependency

products_router = APIRouter(prefix="/products", tags=["Products"])


@products_router.get("/")
async def list_products(products: ProductsServiceDependency, params: QueryParamsDependency):
    return products.get_all(params)

@products_router.get("/search")
async def search_products(products: ProductsServiceDependency, search: SearchEngineDependency):
    return products.search(search)

@products_router.get("/autocomplete")
async def autocomplete_products(products: ProductsServiceDependency, search: SearchEngineDependency):
    results = products.autocomplete(search)
    return {"results": results}

@products_router.get("/{id}")
async def get_product(id: PydanticObjectId, products: ProductsServiceDependency):
    return products.get_one(id) 


@products_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(product: BaseProduct, products:  ProductsServiceDependency, security: SecurityDependency):
    """
    Staff members and admins only!
    """
    # Check current authenticated user is staff or admin
    security.is_staff_or_raise

    result = products.create_one(product, PydanticObjectId(security.auth_user_id))
    if result.acknowledged:
        return {"result message": f"Product created with id: {result.inserted_id}"}
    else:
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": f"An unexpected error ocurred while creating product"},
            )

@products_router.patch("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_product(
    id: PydanticObjectId,
    product: ProductUpdateData,
    products: ProductsServiceDependency,
    security: SecurityDependency
    ):
    """
    Staff members and admins only!
    """
    existing_product = products.get_one(id)
    security.modify_product_permission(existing_product["staff_id"])

    result = products.update_one(id, product) 

    return {"message": "Product succesfully updated","updated product": result}
 
  
@products_router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_product(id: PydanticObjectId, products: ProductsServiceDependency, security: SecurityDependency):
    """
    Admins only!
    """
    security.is_admin_or_raise
    result = products.delete_one(id)
   
    return {"message": "Product succesfully deleted", "deleted product": result}
  

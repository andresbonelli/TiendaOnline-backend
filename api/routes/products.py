__all__ = ["products_router"]

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic_mongo import PydanticObjectId
from datetime import datetime

from ..models import Product, ProductFromDB, UpdateProductData
from ..services import ProductsServiceDependency, AuthServiceDependency

products_router = APIRouter(prefix="/products", tags=["Products"])


@products_router.get("/")
async def list_products(products: ProductsServiceDependency):
    return products.get_all()


@products_router.get("/{id}")
async def get_product(id: PydanticObjectId, products: ProductsServiceDependency):
    return products.get_one(id) or JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Product with id: {id} was not found."},
        )

@products_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(product: Product, products:  ProductsServiceDependency, auth: AuthServiceDependency):
    assert (
        auth.is_admin or auth.is_staff
    ), "Only admins and sellers can create products"
    result = products.create_one(product)
    return {"result message": f"Product {product.name} created with id: {result.inserted_id}"}

@products_router.patch("/{id}")
async def update_product(id: PydanticObjectId, product_data: UpdateProductData, products: ProductsServiceDependency, auth: AuthServiceDependency):
    assert (
        auth.is_admin or auth.is_staff
    ), "Only admins and sellers can modify products"
    result = products.update_one(id, product_data) 
    if result:
        return {"result message": "Product succesfully updated",
                "updated product": ProductFromDB.model_validate(result).model_dump()}
    else:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"Product with id: {id} was not found."},
            )
    
@products_router.delete("/{id}")
async def delete_product(id: PydanticObjectId, products: ProductsServiceDependency, auth: AuthServiceDependency):
    assert (auth.is_admin), "Only admins can delete products"
    result = products.delete_one(id)
    if result:
        return {"result message": "Product succesfully deleted",
                "deleted product": ProductFromDB.model_validate(result).model_dump()}
    else:
        return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"Product with id: {id} was not found."},
            )

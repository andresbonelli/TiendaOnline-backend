__all__ = ["products_router"]

from fastapi import File, UploadFile, status, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from pydantic_mongo import PydanticObjectId
import os
import uuid

from ..config import PUBLIC_HOST_URL
from ..models import BaseProduct, ProductUpdateData, ProductDetails
from ..services import ProductsServiceDependency, SecurityDependency
from ..__common_deps import QueryParamsDependency, SearchEngineDependency

products_router = APIRouter(prefix="/products", tags=["Products"])


@products_router.get("/")
async def list_products(
    products: ProductsServiceDependency, params: QueryParamsDependency
):
    return products.get_all(params)


@products_router.get("/search")
async def search_products(
    products: ProductsServiceDependency, search: SearchEngineDependency
):
    return products.search(search)


@products_router.get("/autocomplete")
async def autocomplete_products(
    products: ProductsServiceDependency,
    search: SearchEngineDependency,
    response: Response,
):
    results = products.autocomplete(search=search, response=response)
    return {"results": results}


@products_router.get("/{id}")
async def get_product(id: PydanticObjectId, products: ProductsServiceDependency):
    return products.get_one(id).model_dump()


@products_router.get("/get_by_staff/{id}")
async def get_products_by_staff_id(
    id: PydanticObjectId,
    products: ProductsServiceDependency,
    security: SecurityDependency,
):
    """
    Authenticaded staff members and admins only!
    """
    security.check_user_permission(id)
    return products.find_from_staff_id(id)


@products_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product: BaseProduct,
    products: ProductsServiceDependency,
    security: SecurityDependency,
):
    """
    Staff members and admins only!
    """
    # Check current authenticated user is staff or admin
    security.is_staff_or_raise

    result = products.create_one(product, PydanticObjectId(security.auth_user_id))
    if result.acknowledged:
        return {
            "message": "Product succesfully created",
            "inserted_id": f"{result.inserted_id}",
        }
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
    security: SecurityDependency,
):
    """
    Authenticaded staff members and admins only!
    """
    existing_product = products.get_one(id)
    security.check_user_permission(existing_product.staff_id)
    result = products.update_one(id, product)
    return {"message": "Product succesfully updated", "product": result}


@products_router.post("/upload_image/{id}")
async def upload_product_image(
    id: PydanticObjectId,
    products: ProductsServiceDependency,
    security: SecurityDependency,
    file: UploadFile = File(...),
):
    """
    Authenticaded staff members and admins only!
    """
    existing_product = products.get_one(id)
    security.check_user_permission(existing_product.staff_id)
    image_name = f"{uuid.uuid4()}.jpg"
    save_directory = os.path.join(
        os.path.dirname(__file__), "..", "..", "static", "images", "products", str(id)
    )
    os.makedirs(save_directory, exist_ok=True)
    file_content = await file.read()
    file_path = os.path.join(save_directory, image_name)
    with open(file_path, "wb") as f:
        f.write(file_content)
    # Destructure Product details to avoid ovewriting
    existing_product_details = (
        ProductDetails.model_dump(existing_product.details)
        if existing_product.details
        else {}
    )
    existing_product_details["image_list"] = (
        existing_product.details.image_list
        if "details" in existing_product and "image_list" in existing_product.details
        else [existing_product.image] if existing_product.image else []
    )
    image_url = f"{PUBLIC_HOST_URL}/static/images/products/{id}/{image_name}"
    updated_product = ProductUpdateData(
        image=image_url,
        details={
            **existing_product_details,
            "image_list": [*existing_product_details["image_list"], image_url],
        },
    )
    return products.update_one(id=id, product=updated_product)


@products_router.delete("/{id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_product(
    id: PydanticObjectId,
    products: ProductsServiceDependency,
    security: SecurityDependency,
):
    """
    Admins only!
    """
    security.check_user_permission(security.auth_user_id)
    result = products.delete_one(id)
    return {"message": "Product succesfully deleted", "product": result}

__all__ = ["orders_router"]

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic_mongo import PydanticObjectId

from ..__common_deps import QueryParams, QueryParamsDependency
from ..models import Order, UpdationProduct
from ..services import (
    OrdersServiceDependency,
    ProductsServiceDependency,
    SecurityDependency,
)

orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@orders_router.get("/get_all")
def get_all_orders(
    orders: OrdersServiceDependency,
    security: SecurityDependency,
    params: QueryParamsDependency,
):
    security.is_admin
    return orders.get_all(params)


@orders_router.get("/get_by_seller/{id}")
def get_orders_by_seller_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    auth_user_id = security.auth_user_id
    assert (
        auth_user_id == id or security.auth_user_role == "admin"
    ), "User does not have access to this orders"

    # BUG: Order does not have "staff_id" !!!
    params = QueryParams(filter=f"staff_id={id}")
    return orders.get_all(params)


@orders_router.get("/get_by_customer/{id}")
def get_orders_by_customer_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    auth_user_id = security.auth_user_id
    assert (
        auth_user_id == id or security.auth_user_role == "admin"
    ), "User does not have access to this orders"

    params = QueryParams(filter=f"customer_id={id}")
    return orders.get_all(params)


@orders_router.get("/get_by_product/{id}")
def get_orders_by_product_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    auth_user_id = security.auth_user_id
    params = QueryParams(filter=f"product_id={id}")
    return orders.get_all(params)


@orders_router.post("/")
def create_order(
    order: Order,
    orders: OrdersServiceDependency,
    products: ProductsServiceDependency,
    security: SecurityDependency,
):
    security.is_customer_or_raise
    product = products.get_one(order.product_id)
    assert product.get("quantity", 0) >= order.quantity, "Product is out of stock"
    products.update_one(
        order.product_id,
        UpdationProduct(stock=product["stock"] - order.quantity),
    )
    result = orders.create_one(order)
    if result.acknowledged:
        return {"result message": f"Order created with id: {result.inserted_id}"}
    else:
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": f"An unexpected error ocurred while creating product"},
            )

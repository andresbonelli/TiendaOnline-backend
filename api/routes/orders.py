__all__ = ["orders_router"]

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic_mongo import PydanticObjectId

from datetime import datetime

from ..__common_deps import QueryParams, QueryParamsDependency
from ..models import BaseOrder, OrderCreateData, ProductUpdateData
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
    """
    Admins only!
    """
    security.is_admin_or_raise
    return orders.get_all(params)

@orders_router.get("/get_by_seller/{id}")
def get_orders_by_seller_id(
    id: PydanticObjectId,
    security: SecurityDependency,
    orders: OrdersServiceDependency,
    products: ProductsServiceDependency
):
    """
    Authenticated staff member only!
    """
    auth_user_id = security.auth_user_id
    assert (
        auth_user_id == str(id) or security.auth_user_role == "admin"
    ), "User does not have access to this orders"
    return orders.find_from_staff_id(id)
    # product_search_params = QueryParams(filter=f"staff_id={id}")
    # seller_products: list[dict] = products.get_all(product_search_params)

    # return [orders.get_all(QueryParams(filter=f"product_id={product["id"]}")) for product in seller_products]

@orders_router.get("/get_by_customer/{id}")
def get_orders_by_customer_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    """
    Authenticated customer only!
    """
    auth_user_id = security.auth_user_id
    assert (
        auth_user_id == str(id) or security.auth_user_role == "admin"
    ), "User does not have access to this orders"

    params = QueryParams(filter=f"customer_id={id}")
    return orders.get_all(params)

@orders_router.get("/get_by_product/{id}")
def get_orders_by_product_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    """
    Staff members and admins only!
    """
    security.is_staff_or_raise
    params = QueryParams(filter=f"product_id={id}")
    return orders.get_all(params)

# Purchase order for a single product. 
@orders_router.post("/")
def create_order(
    order: BaseOrder,
    orders: OrdersServiceDependency,
    products: ProductsServiceDependency,
    security: SecurityDependency,
):
    """
    Customers only!
    """
    security.is_customer_or_raise
    
    existing_product = products.get_one(order.product_id)
    assert existing_product.get("stock", 0) >= order.quantity, "Product is out of stock"
    
    #Prepare Order
    new_order: dict = {
        "customer_id": PydanticObjectId(security.auth_user_id),
        "product_id": PydanticObjectId(order.product_id),
        "quantity": order.quantity,
        "total_price": existing_product["price"] * order.quantity,
        "created_at": datetime.now()
    }
    
    #Store Order in database
    result = orders.create_one(new_order)
    
    #Update product stock
    product_to_update = ProductUpdateData(
        stock=existing_product["stock"] - order.quantity,
        modified_at=datetime.now()
        )
    products.update_one(
        order.product_id,
        product_to_update,
    )
    
    if result.acknowledged:
        return {"result message": f"Order created with id: {result.inserted_id}"}
    else:
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": f"An unexpected error ocurred while creating order"},
            )

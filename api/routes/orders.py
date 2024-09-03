__all__ = ["orders_router"]

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic_mongo import PydanticObjectId
from datetime import datetime

from ..__common_deps import QueryParamsDependency
from ..models import BaseOrder, OrderStatus, ProductUpdateData, OrderUpdateData
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

@orders_router.get("/get_by_customer/{id}")
def get_orders_by_customer_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    """
    Authenticated customer only!
    """
    security.check_user_permission(str(id))
    return orders.find_from_customer_id(id)
  
@orders_router.get("/get_by_product/{id}")
def get_orders_by_product_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    """
    Staff members and admins only!
    """
    security.is_staff_or_raise
    return orders.find_from_product_id(id)

@orders_router.get("/get_by_staff/{id}")
def get_orders_by_staff_id(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    """
    Authenticated staff member only!
    """
    security.check_user_permission(str(id))
    return orders.find_from_staff_id(id)

# Purchase order (multiple products). 
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
    
    for product in order.products:
        existing_product = products.get_one(product.product_id)
        if existing_product.get("stock", 0) <= product.quantity:
            raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Product {product.product_id} is out of stock"
                ) 
    
    #Prepare Order
    new_order: dict = {
        "customer_id": PydanticObjectId(security.auth_user_id),
        "products": [
                {
                "product_id": PydanticObjectId(product.product_id),
                "quantity": product.quantity
                }
                for product in order.products
            ],
        "status": OrderStatus.pending,
        "created_at": datetime.now()
    }
    
    #Store Order in database
    result = orders.create_one(new_order)
    
    #Update product stock
    for product in new_order["products"]:
        existing_product = products.get_one(product["product_id"])
        product_to_update = ProductUpdateData(
            stock=existing_product["stock"] - product["quantity"],
            modified_at=datetime.now()
            )
        products.update_one(
            product["product_id"],
            product_to_update,
        )
    
    if result.acknowledged:
        return {"result message": f"Order created with id: {result.inserted_id}"}
    else:
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": f"An unexpected error ocurred while creating order"},
            )

@orders_router.patch("/complete/{id}")
def complete_order(
    id: PydanticObjectId, security: SecurityDependency, orders: OrdersServiceDependency
):
    """
    Authenticated customer only!
    """
    existing_order = orders.get_one(id)
    
    security.check_user_permission(existing_order["customer_id"])
    
    total_price = orders.calculate_total_price(id)
    
    result = orders.update_one(id, OrderUpdateData(
        status=OrderStatus.completed,
        total_price=total_price[0]
        ))
    
    return {"message": "Order succesfully fulfilled","Completed order": result}
    
    
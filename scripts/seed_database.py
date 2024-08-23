from api.models import UserRegisterData, BaseOrder, ProductCreateData, OrderCreateData
from api.services import AuthService, OrdersService, ProductsService, UsersService
from pydantic_mongo import PydanticObjectId
from datetime import datetime

# Create two basic users

users = [
    {
        "username": "Vendedor1",
        "email": "a@a.com",
        "password": "123",
        "role": "staff",
    },
    {
        "username": "Vendedor2",
        "email": "c@c.com",
        "password": "123",
        "role": "staff",
    },
    {
        "username": "Comprador",
        "email": "b@b.com",
        "password": "123",
        "role": "customer",
    },
]

print("Creating users...")
users_ids = []
for user in users:
    hash_password = AuthService.get_password_hash(user["password"])
    insertion_user = UserRegisterData.model_validate(user)
    result = UsersService.create_one(insertion_user, hash_password=hash_password)
    users_ids.append(result.inserted_id)

# Create some products

products = [
    {
        "staff_id": PydanticObjectId(users_ids[0]),
        "name": "Product 1",
        "description": "Product 1 description",
        "price": 100,
        "stock": 10,
        "created_at": datetime.now()
    },
    {
        "staff_id": PydanticObjectId(users_ids[0]),
        "name": "Product 2",
        "description": "Product 2 description",
        "price": 200,
        "stock": 20,
        "created_at": datetime.now()
    },
    {
        "staff_id": PydanticObjectId(users_ids[0]),
        "name": "Product 3",
        "description": "Product 3 description",
        "price": 300,
        "stock": 30,
        "created_at": datetime.now()
    },
    {
        "staff_id": PydanticObjectId(users_ids[0]),
        "name": "Product 4",
        "description": "Product 4 description",
        "price": 400,
        "stock": 40,
        "created_at": datetime.now()
    },
    {
        "staff_id": PydanticObjectId(users_ids[0]),
        "name": "Product 5",
        "description": "Product 5 description",
        "price": 500,
        "stock": 50,
        "created_at": datetime.now()
    },
    {
        "staff_id": PydanticObjectId(users_ids[0]),
        "name": "Product 6",
        "description": "Product 6 description",
        "price": 600,
        "stock": 60,
        "created_at": datetime.now()
    },
    {
        "staff_id": PydanticObjectId(users_ids[1]),
        "name": "Product 7",
        "description": "Product 7 description",
        "price": 700,
        "stock": 70,
        "created_at": datetime.now()
    },
    {
        "staff_id": PydanticObjectId(users_ids[1]),
        "name": "Product 8",
        "description": "Product 8 description",
        "price": 800,
        "stock": 80,
        "created_at": datetime.now()
    },
    {
        "staff_id": PydanticObjectId(users_ids[1]),
        "name": "Product 9",
        "description": "Product 9 description",
        "price": 900,
        "stock": 90,
        "created_at": datetime.now()
    },
    {
        "staff_id": PydanticObjectId(users_ids[1]),
        "name": "Product 10",
        "description": "Product 10 description",
        "price": 1000,
        "stock": 100,
        "created_at": datetime.now()
    },
]


print("Creating products...")
product_ids = []
for product in products:
    ProductCreateData.model_validate(product)
    result = ProductsService.create_one(product)
    product_ids.append(result.inserted_id)

# Create some orders

orders = [
    {
        "customer_id": PydanticObjectId(users_ids[2]),
        "product_id": PydanticObjectId(product_ids[9]),
        "quantity": 1,
        "total_price": products[9]["price"] * 1,
        "created_at": datetime.now()
    },
    {
        "customer_id": PydanticObjectId(users_ids[2]),
        "product_id": PydanticObjectId(product_ids[5]),
        "quantity": 2,
        "total_price": products[5]["price"] * 2,
        "created_at": datetime.now()
    },
]

print("Creating orders...")
for order in orders:
    OrderCreateData.model_validate(order)
    OrdersService.create_one(order)

print("Done!")

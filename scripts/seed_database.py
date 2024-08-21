from api.models import UserRegisterData, BaseOrder, BaseProduct
from api.services import AuthService, OrdersService, ProductsService, UsersService

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
        "staff_id": users_ids[0],
        "name": "Product 1",
        "description": "Product 1 description",
        "price": 100,
        "stock": 10,
    },
    {
        "staff_id": users_ids[0],
        "name": "Product 2",
        "description": "Product 2 description",
        "price": 200,
        "stock": 20,
    },
    {
        "staff_id": users_ids[0],
        "name": "Product 3",
        "description": "Product 3 description",
        "price": 300,
        "stock": 30,
    },
    {
        "staff_id": users_ids[0],
        "name": "Product 4",
        "description": "Product 4 description",
        "price": 400,
        "stock": 40,
    },
    {
        "staff_id": users_ids[0],
        "name": "Product 5",
        "description": "Product 5 description",
        "price": 500,
        "stock": 50,
    },
    {
        "staff_id": users_ids[0],
        "name": "Product 6",
        "description": "Product 6 description",
        "price": 600,
        "stock": 60,
    },
    {
        "staff_id": users_ids[1],
        "name": "Product 7",
        "description": "Product 7 description",
        "price": 700,
        "stock": 70,
    },
    {
        "staff_id": users_ids[1],
        "name": "Product 8",
        "description": "Product 8 description",
        "price": 800,
        "stock": 80,
    },
    {
        "staff_id": users_ids[1],
        "name": "Product 9",
        "description": "Product 9 description",
        "price": 900,
        "stock": 90,
    },
    {
        "staff_id": users_ids[1],
        "name": "Product 10",
        "description": "Product 10 description",
        "price": 1000,
        "stock": 100,
    },
]


print("Creating products...")
product_ids = []
for product in products:
    insertion_product = BaseProduct.model_validate(product)
    result = ProductsService.create_one(insertion_product)
    product_ids.append(result.inserted_id)

# Create some orders

orders = [
    {
        "customer_id": users_ids[2],
        "product_id": product_ids[9],
        "price": 900,
        "quantity": 1,
    },
    {
        "customer_id": users_ids[2],
        "product_id": product_ids[5],
        "price": 496,
        "quantity": 2,
    },
]

print("Creating orders...")
for order in orders:
    insertion_order = BaseOrder.model_validate(order)
    OrdersService.create_one(insertion_order)

print("Done!")

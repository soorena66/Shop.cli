from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from FastAPI_models import db, User, Product, Order

app = FastAPI(
    title="Online Store - FastAPI",
    description="RESTful API project using FastAPI, Peewee ORM, and SQLite",
    version="2.0.0"
)

@app.get('/', tags=["Root"])
def root():
    """Welcome page"""
    return {
        "message": "Welcome to the Online Store API!",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# --- Database connection middleware ---
@app.middleware("http")
async def db_middleware(request, call_next):
    if db.is_closed():
        db.connect()
    try:
        response = await call_next(request)
        return response
    finally:
        if not db.is_closed():
            db.close()


# --- Pydantic Models (for request validation and auto-documentation) ---

class UserRegister(BaseModel):
    username: str
    password: str
    is_admin: Optional[bool] = False

class ProductCreate(BaseModel):
    name: str
    price: float
    stock: int
    category: Optional[str] = None
    brand: Optional[str] = None

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = 1


# --- User Endpoints ---

@app.get('/users', tags=["Users"])
def get_users():
    """Retrieve a list of all users"""
    users_list = []
    for user in User.select():
        users_list.append({
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "is_active": user.is_active
        })
    return {"users": users_list}

@app.post('/users/register', status_code=status.HTTP_201_CREATED, tags=["Users"])
def register_user(user_data: UserRegister):
    """Register a new user"""
    if User.get_or_none(User.username == user_data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User.create(
        username=user_data.username,
        password=user_data.password,  # In production, use password hashing!
        is_admin=user_data.is_admin
    )
    return {"message": "User registered successfully", "user_id": new_user.id}


# --- Product Endpoints ---

@app.get('/products', tags=["Products"])
def get_products():
    """Retrieve all products in the store"""
    return {"products": list(Product.select().dicts())}

@app.post('/products', status_code=status.HTTP_201_CREATED, tags=["Products"])
def create_product(product: ProductCreate):
    """Add a new product to inventory"""
    p = Product.create(**product.dict())
    return {"message": "Product created successfully", "product_id": p.id}

@app.delete('/products/{product_id}', tags=["Products"])
def delete_product(product_id: int):
    """Delete a product by ID"""
    product = Product.get_or_none(Product.id == product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.delete_instance()
    return {"message": "Product deleted successfully", "product_id": product_id}


# --- Order Endpoints ---

@app.get('/orders', tags=["Orders"])
def get_orders():
    """Retrieve all registered orders"""
    orders_list = []
    for order in Order.select():
        orders_list.append({
            "order_id": order.id,
            "user": order.user.username,
            "product": order.product.name,
            "quantity": order.quantity,
            "total_price": order.total_price,
            "status": order.status
        })
    return {"orders": orders_list}

@app.post('/orders', status_code=status.HTTP_201_CREATED, tags=["Orders"])
def create_order(order_data: OrderCreate):
    """Create a new order and update stock automatically"""
    user = User.get_or_none(User.id == order_data.user_id)
    product = Product.get_or_none(Product.id == order_data.product_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.stock < order_data.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock for this product")
    
    # Calculate total price and update stock

    total = product.price * order_data.quantity
    product.stock -= order_data.quantity
    product.save()
    
    new_order = Order.create(
        user=user,
        product=product,
        quantity=order_data.quantity,
        total_price=total,
        status="Pending"
    )
    
    return {
        "message": "Order placed successfully",
        "order_id": new_order.id,
        "total_price": total,
        "remaining_stock": product.stock
    }

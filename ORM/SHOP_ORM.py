from peewee import *

db = SqliteDatabase('forooshgah.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    is_admin = BooleanField(default=False)
    is_active = IntegerField(default=1)  # Soft delete: 1 = Active, 0 = Inactive

class Product(BaseModel):
    name = CharField()
    category = CharField()
    brand = CharField()
    price = DecimalField(max_digits=10, decimal_places=2)
    stock = IntegerField(default=0)

class Order(BaseModel):
    user = ForeignKeyField(User, backref='orders')
    total_price = DecimalField(max_digits=10, decimal_places=2)
    status = CharField(default='Pending')

class OrderItem(BaseModel):
    order = ForeignKeyField(Order, backref='items')
    product = ForeignKeyField(Product, backref='order_items')
    quantity = IntegerField()
    price = DecimalField(max_digits=10, decimal_places=2)

class ShopManager:
    def __init__(self):
        db.connect()
        db.create_tables([User, Product, Order, OrderItem], safe=True)

    def register_user(self, username, password, is_admin=False):
        try:
            User.create(username=username, password=password, is_admin=is_admin, is_active=1)
            return True
        except IntegrityError:
            return False

    def login_user(self, username, password):
        try:
            user = User.get((User.username == username) & (User.password == password) & (User.is_active == 1))
            return {"id": user.id, "username": user.username, "is_admin": user.is_admin}
        except DoesNotExist:
            return None

    def search_products(self, keyword):
        query = Product.select().where(
            (Product.name.icontains(keyword)) |
            (Product.category.icontains(keyword)) |
            (Product.brand.icontains(keyword))
        )
        return [{"id": p.id, "name": p.name, "category": p.category, "brand": p.brand, "price": float(p.price), "stock": p.stock} for p in query]

    def get_categories(self):
        query = Product.select(Product.category).distinct()
        return [p.category for p in query]

    def get_products_by_category(self, category_name):
        query = Product.select().where(Product.category == category_name)
        return [{"id": p.id, "name": p.name, "category": p.category, "brand": p.brand, "price": float(p.price), "stock": p.stock} for p in query]

    def add_product(self, name, category, brand, price, stock):
        Product.create(name=name, category=category, brand=brand, price=price, stock=stock)

    def update_product_stock(self, product_id, new_stock):
        try:
            product = Product.get_by_id(product_id)
            product.stock = new_stock
            product.save()
            return True
        except DoesNotExist:
            return False

    def soft_delete_user(self, user_id):
        try:
            user = User.get_by_id(user_id)
            user.is_active = 0
            user.save()
            return True
        except DoesNotExist:
            return False

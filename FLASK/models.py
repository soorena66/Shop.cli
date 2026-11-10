from peewee import *

db = SqliteDatabase('forooshgah.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    is_admin = BooleanField(default=False)
    is_active = IntegerField(default=1)  # Soft Delete support

class Product(BaseModel):
    name = CharField()
    price = FloatField()
    stock = IntegerField()
    category = CharField(null=True)
    brand = CharField(null=True)
    is_active = BooleanField(default=True)

class Order(BaseModel):
    user = ForeignKeyField(User, backref='orders')
    product = ForeignKeyField(Product, backref='orders')
    quantity = IntegerField(default=1)
    total_price = FloatField()
    status = CharField(default='Pending')

def initialize_db():
    db.connect()
    db.create_tables([User, Product, Order], safe=True)
    db.close()



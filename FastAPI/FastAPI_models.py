from peewee import SqliteDatabase, Model, CharField, IntegerField, FloatField, ForeignKeyField, BooleanField

# Initialize database
db = SqliteDatabase('Store.db')

class User(Model):
    username = CharField(max_length=50, unique=True)
    password = CharField(max_length=50)
    is_admin = BooleanField(default=False)
    is_active = IntegerField(default=1)

    class Meta:
        database = db
        db_table = 'u'  # Short table name

class Product(Model):
    name = CharField(max_length=50)
    price = FloatField()
    stock = IntegerField()
    category = CharField(max_length=50, null=True)
    brand = CharField(max_length=50, null=True)

    class Meta:
        database = db
        db_table = 'p'

class Order(Model):
    user = ForeignKeyField(User, backref='orders')
    product = ForeignKeyField(Product, backref='orders')
    quantity = IntegerField(default=1)
    total_price = FloatField()
    status = CharField(max_length=20, default='Pending')

    class Meta:
        database = db
        db_table = 'o'

# Create tables if they don't exist
db.create_tables([User, Product, Order])

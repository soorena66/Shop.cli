from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Product, Order, initialize_db

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.before_request
def before_request():
    db.connect()

@app.teardown_request
def teardown_request(exc):
    if not db.is_closed():
        db.close()

@app.route('/')
def index():
    query = request.args.get('q', '')
    if query:
        products = Product.select().where(Product.name.contains(query))
    else:
        products = Product.select()
    return render_template('index.html', products=products, query=query)
    
@app.route('/orders')
def orders():
    if not session.get('user_id'):
        flash('Please login first to view your orders.', 'warning')
        return redirect(url_for('login'))
        
    user_orders = Order.select().where(Order.user == session['user_id'])
    return render_template('orders.html', orders=user_orders)

@app.route('/create', methods=['GET', 'POST'])
def create_product():
    if not session.get('user_id') or not session.get('is_admin'):
        flash('Access denied! Admin privileges required.', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        stock = request.form.get('stock')
        category = request.form.get('category')
        brand = request.form.get('brand')
        
        if not name or not price or not stock:
            flash('Please fill in all required fields.', 'warning')
            return redirect(url_for('create_product'))
            
        Product.create(
            name=name,
            price=float(price),
            stock=int(stock),
            category=category,
            brand=brand
        )
        flash('Product created successfully!', 'success')
        return redirect(url_for('index'))
        
    return render_template('create.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    if not session.get('user_id') or not session.get('is_admin'):
        flash('Access denied! Admin privileges required.', 'danger')
        return redirect(url_for('index'))
        
    product = Product.get_or_none(Product.id == id)
    if not product:
        flash('Product not found!', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.category = request.form.get('category')
        product.brand = request.form.get('brand')
        product.save()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('index'))
        
    return render_template('update.html', product=product)

@app.route('/order/create/<int:product_id>', methods=['POST'])
def create_order(product_id):
    if not session.get('user_id'):
        flash('Please login first to place an order.', 'warning')
        return redirect(url_for('login'))
        
    product = Product.get_or_none(Product.id == product_id)
    if not product:
        flash('Product not found!', 'danger')
        return redirect(url_for('index'))
        
    quantity = int(request.form.get('quantity', 1))
    
    if product.stock < quantity:
        flash('Not enough stock available!', 'danger')
        return redirect(url_for('index'))
        
    product.stock -= quantity
    product.save()
    
    Order.create(
        user=session['user_id'],
        product=product,
        quantity=quantity,
        total_price=product.price * quantity
    )
    
    flash('Order placed successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get_or_none(User.username == username)
        
        if user and user.password == password and user.is_active:
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.get_or_none(User.username == username):
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
            
        User.create(username=username, password=password, is_admin=False)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.connect(reuse_if_open=True)
    db.create_tables([User, Product, Order], safe=True)
    
    admin_user, created = User.get_or_create(
        username='admin',
        defaults={
            'password': 'password',
            'is_admin': True,
            'is_active': 1
        }
    )
    
    if not admin_user.is_admin:
        admin_user.is_admin = True
        admin_user.save()
        print("Admin privileges granted to 'admin' user!")

    app.run(debug=True, port=5000)

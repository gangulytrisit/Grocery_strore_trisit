from database import User, Category, Product, CartItem, Order, db
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, login_required, LoginManager, current_user, logout_user
from datetime import datetime



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
app.config['SECRET_KEY'] = '8c6eb0a487d1e27c8253f1c7'
db.init_app(app)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_id(id):
  if User.query.get(id):
    return User.query.get(id) 



with app.app_context():
     db.create_all()




# route for home or / 

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')






#dummy shopping page 

@app.route('/shopping')
def shopping_page():
    return render_template('shopping.html')







#registration page

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        # user registration data from the form
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        if username == "admin" and password == "admin":
       
            admin_exists = User.query.filter_by(username="admin").first()
            if admin_exists:
                flash('An admin account already exists. Registration not allowed.', 'error')
                return redirect(url_for('register_page'))
            else:
                new_admin = User(username=username, password=password, email=email, is_admin=True)
                db.session.add(new_admin)
                db.session.commit()
                flash('Admin account created successfully.', 'success')
                return redirect(url_for('login_page'))

   
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another username.')
        else:
            new_user = User(username=username, password=password, email=email)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login_page'))

    return render_template('register.html')







#login page

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == "admin" and password == "admin":
          
         
            admin_exists = User.query.filter_by(username="admin").first()
            if admin_exists:
                login_user(admin_exists)
                flash('Logged in as admin', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Admin account not found.')
                return redirect(url_for('login_page'))

        else:
            user = User.query.filter_by(username=username).first()

            if user and user.password == password:
          
                login_user(user)
                flash('Logged in successfully', 'success')
                return redirect(url_for('user_dashboard'))
            else:
                flash('Login failed. Please check your username and password.')
                return redirect(url_for('login_page'))

    return render_template('login.html')






#admin dashboard

@app.route('/admin_dashbord')
@login_required
def admin_dashboard():
    categories=Category.query.all()
    return render_template('admin_dashboard.html',current_user=current_user.username, categories=categories)






#logout route

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("login_page"))






# Route for user dashboard


@app.route('/user_dashboard')
@login_required
def user_dashboard():
    
    categories = Category.query.all()
    products = Product.query.all()

   
    user_cart = CartItem.query.filter_by(user_id=current_user.id).all()

    
    cart_items_by_product_id = {item.product_id: item for item in user_cart}

    
    for product in products:
        if product.id in cart_items_by_product_id:
            
            product.unit_left = product.unit - cart_items_by_product_id[product.id].quantity
        else:
           
            product.unit_left = product.unit

    return render_template('user_dashboard.html', current_user=current_user.username, categories=categories, products=products, user_id=current_user.id)






#routes for admin account

@app.route('/admin_dashboard/account')
@login_required
def admin_account():
    return render_template('admin_account.html', current_user=current_user.username)







#route for add category(admin)

@app.route('/category/add_cat')
@login_required
def add_cat():
    return render_template('add_cat.html')
    





#routes of info for each category  
 

@app.route('/category/<int:category_id>/info_cat')
@login_required
def info_cat(category_id):
    category = Category.query.get(category_id)
    return render_template('info_cat.html', category=category)





#route for add product 


@app.route('/category/<int:category_id>/add_pro', methods=['GET', 'POST'])
@login_required
def add_pro(category_id):
    category = Category.query.get(category_id)
    if request.method == 'POST':

        

        product_name = request.form['product_name']
        unit = request.form['unit']
        rate = request.form['rate']
        
        
        manufacture_date_str = request.form['manufacture_date']
        expiry_date_str = request.form['expiry_date']
        
        if manufacture_date_str:
            manufacture_date = datetime.strptime(manufacture_date_str, '%d-%m-%Y').date()
        else:
            manufacture_date = None  
        
        if expiry_date_str:
            expiry_date = datetime.strptime(expiry_date_str, '%d-%m-%Y').date()
        else:
            expiry_date = None  

       
        new_product = Product(
            name=product_name,
            unit=unit,
            rate_per_unit=rate,
            manufacture_date=manufacture_date,
            expiry_date=expiry_date,
            category_id=category.id  
        )

       
        db.session.add(new_product)
        db.session.commit()


        return redirect(url_for('info_cat', category_id=category_id))

    return render_template('add_pro.html', category=category)





#route for edit product


@app.route('/product/<int:id>/edit_pro', methods=['GET', 'POST'])
@login_required
def edit_pro(id):
    product = Product.query.get(id)

    if request.method == 'POST':
      
        product.name = request.form['product_name']
        product.unit = request.form['unit']
        product.rate_per_unit = float(request.form['rate_per_unit'])

        manufacture_date_str = request.form['manufacture_date']
        expiry_date_str = request.form['expiry_date']
        
        if manufacture_date_str:
            manufacture_date = datetime.strptime(manufacture_date_str, '%d-%m-%Y').date()
        else:
            manufacture_date = None  
        
        if expiry_date_str:
            expiry_date = datetime.strptime(expiry_date_str, '%d-%m-%Y').date()
        else:
            expiry_date = None  
        
        product.manufacture_date = manufacture_date
        product.expiry_date = expiry_date


        db.session.commit()

      
        return redirect(url_for('info_cat', category_id=product.category_id))

    return render_template('edit_pro.html', product=product)





#route for delete Product

@app.route('/product/<int:id>/delete_pro', methods=['POST'])
@login_required
def delete_pro(id):
    
    product = Product.query.get(id)
    
    if product:
        
        db.session.delete(product)
        db.session.commit()
    
    return redirect(url_for('info_cat', category_id=product.category_id))






#route for Edit category(admin)


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_cat(category_id):
   
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
       
        new_name = request.form['new_name']
        new_description = request.form['category_description']  

       
        category.name = new_name
        category.description = new_description

        
        db.session.commit()

        flash('Category updated successfully')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_cat.html', category=category)  





#route for delete category(admin)

@app.route('/category/<int:category_id>/delete_cat', methods=['POST'])
@login_required
def delete_cat(category_id):
    
    category = Category.query.get_or_404(category_id)

  
    db.session.delete(category)
    db.session.commit()

    flash('Category deleted successfully')
    return redirect(url_for('admin_dashboard'))





#route for add category

@app.route('/category/add_cat', methods=['POST'])
def add_category_post():
    if request.method == 'POST':
        category_name = request.form.get('category_name')
        category_description = request.form.get('category_description')

        if not category_name:
            flash('Category name is required')
            return redirect(url_for('add_cat'))

       
        existing_category = Category.query.filter_by(name=category_name).first()
        if existing_category:
            flash('Category already exists')
            return redirect(url_for('add_cat'))

        
        new_category = Category(name=category_name, description=category_description)
        db.session.add(new_category)
        db.session.commit()
        flash('New category successfully created')

        return redirect(url_for('admin_dashboard'))





#  route for user add_cart 

@app.route('/user_cart/<int:user_id>')
def user_cart(user_id):
    user = User.query.get(user_id)


    carts = CartItem.query.filter_by(user_id=user_id).all()

    total_sum = sum([cart.product.rate_per_unit * cart.quantity for cart in carts])
    if current_user.id==user_id:
        return render_template('user_cart.html', user=user, carts=carts, total_sum=total_sum ,user_id=user_id)
    else:
        return '''you are not authorised to access this route'''





# add to cart route for user


@app.route('/add_to_cart/<int:product_id>', methods=["POST"])
@login_required
def add_to_cart(product_id):
    unit = request.form.get('unit')
    
    
    unit = int(unit)
    
   
    product = Product.query.get(product_id)
        

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    
    if cart_item:
      
        cart_item.quantity += unit
        cart_item.price = cart_item.product.unit * product.rate_per_unit
    else:
  
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=unit,
            price=unit * product.rate_per_unit
        )
    
 
    db.session.add(cart_item)
    db.session.commit()
    
    flash('Product added to cart', 'success')
    return redirect(url_for('user_dashboard', user_id=current_user.id))
   




# checkout page for route


@app.route('/user_checkout', methods=['GET', 'POST'])
@login_required
def user_checkout():
    if request.method == 'GET':

        user_id = current_user.id  
        cart_items = CartItem.query.filter_by(user_id=user_id).all()


        if not cart_items:
            flash('Your cart is empty', 'error')
            return redirect(url_for('user_cart', user_id = current_user.id ))
        

        for cart_item in cart_items:
            order = Order(
                user_id=cart_item.user_id,
                product_id=cart_item.product_id,
                Product_name=cart_item.product.name,
                Product_price=cart_item.price,
                Product_unit=cart_item.quantity,
    
            )
    

            # print(cart_item.product.name)
            
            db.session.add(order)
            db.session.delete(cart_item)

        db.session.commit()
       
        return render_template('user_checkout.html')



#  Route for User order history 



@app.route('/order_history/<int:user_id>')
@login_required
def order_history(user_id):
    
    user_id = current_user.id 
    orders = Order.query.filter_by(user_id=user_id).all()

    return render_template('order_history.html', orders=orders)







# delete from cart option 


@app.route('/delete_from_cart/<int:item_id>', methods=["POST"])
@login_required
def delete_from_cart(item_id):
   
    cart_item = CartItem.query.get(item_id)

    if cart_item:
       
        db.session.delete(cart_item)
        db.session.commit()
        flash('Product removed from cart', 'success')
    else:
        flash('Cart item not found', 'error')

    return redirect(url_for('user_cart', user_id=current_user.id))





# Routes for  Search Products 



@app.route('/search_pro', methods=['GET', 'POST'])
def search_pro():
    if request.method == 'POST':
         category_id = request.form.get('category')
         price_min = request.form.get('min_price')
         price_max = request.form.get('max_price')   
         query = request.form.get('search_query')

         products = Product.query.filter_by(category_id=category_id).filter(Product.name.contains(query))

         if price_min and price_max:
             products = products.filter(Product.rate_per_unit.between(float(price_min), float(price_max)))
         elif price_min:
             products = products.filter(Product.rate_per_unit >= float(price_min))
         elif price_max:
             products = products.filter(Product.rate_per_unit <= float(price_max))

         filtered_products = products.all()

         return render_template('search_pro.html', products=filtered_products)

   
    categories = Category.query.all()
    return render_template('search_pro.html', categories=categories)




 


if __name__ == '__main__':
    app.run(debug=True)
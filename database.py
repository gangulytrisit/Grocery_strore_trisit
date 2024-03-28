from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import *



db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(140), nullable=False , unique=True)
    is_admin = db.Column(db.Boolean(), nullable=False ,default=False)
     
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(250), default='None',nullable=False, unique=True)  

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.Integer,nullable=False)
    manufacture_date = db.Column(db.Date, nullable=True)  
    expiry_date = db.Column(db.Date,nullable=True)
    rate_per_unit = db.Column(db.Float, nullable=False)
    
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('products', lazy=True))

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))  
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float())
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

   

class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    Product_name = db.Column(db.String) 
    Product_price = db.Column(db.Float)  
    Product_unit = db.Column(db.Integer)  
    cart_item_id = db.Column(db.Integer, db.ForeignKey('cart_item.id'))  
    cart_item = db.relationship('CartItem', backref=db.backref('order', lazy=True))



    


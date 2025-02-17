
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime, Boolean, func
from flask_login import UserMixin
from Kursinis import app, db


# Vartotojai 
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)   #nullable=False, default='-'
    email = db.Column(db.String(120), unique=True)     #nullable=False, default='-'
    password = db.Column(db.String(120)) #nullable=False, default='-'
    date_register = db.Column(db.String(120))   #nullable=False
    cookie_id = db.Column(db.String(36), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    account = db.relationship('Account', back_populates='user', uselist=False)    #uselist=False
    cart = db.relationship('Cart', back_populates='user', uselist=False)   #uselist=False???
    orders = db.relationship('Orders', back_populates='user')
    delivery_info = db.relationship('DeliveryInfo', back_populates='user')

# class UserSecond(db.Model):
#     __tablename__ = 'users_second'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120), unique=True)   #nullable=False, default='-'
#     email = db.Column(db.String(120), unique=True)     #nullable=False, default='-'
#     password = db.Column(db.String(120)) #nullable=False, default='-'
#     date_register = db.Column(db.String(120))   #nullable=False
#     cookie_id = db.Column(db.String(36), unique=True, nullable=False)
#     timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    # account = db.relationship('Account', back_populates='user', uselist=False)    #uselist=False
    # cart = db.relationship('Cart', back_populates='user', uselist=False)   #uselist=False???
    # orders = db.relationship('Orders', back_populates='user')
    # delivery_info = db.relationship('DeliveryInfo', back_populates='user')


class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='account')

# class Vartotojas(db.Model, UserMixin):
#     __tablename__ = "vartotojas"
#     id = db.Column(db.Integer, primary_key=True)
#     vardas = db.Column("Vardas", db.String(20), unique=True, nullable=False)
#     el_pastas = db.Column("El. pašto adresas", db.String(120), unique=True, nullable=False)
#     nuotrauka = db.Column(db.String(20), nullable=False, default='default.jpg')
#     slaptazodis = db.Column("Slaptažodis", db.String(60), unique=True, nullable=False)

#     def get_reset_token(self, expires_sec=1800):
#         s = Serializer(app.config['SECRET_KEY'], expires_sec)
#         return s.dumps({'user_id': self.id}).decode('utf-8')

#     @staticmethod
#     def verify_reset_token(token):
#         s = Serializer(app.config['SECRET_KEY'])
#         try:
#             user_id = s.loads(token)['user_id']
#         except:
#             return None
#         return Vartotojas.query.get(user_id)



#Produktai
product_size_association = db.Table('product_size',
    db.Column('products_id', db.Integer, db.ForeignKey('products.id')),
    db.Column('sizes_id', db.Integer, db.ForeignKey('sizes.id'))
)

product_color_association = db.Table('product_color',
    db.Column('products_id', db.Integer, db.ForeignKey('products.id')),
    db.Column('colors_id', db.Integer, db.ForeignKey('colors.id'))
)

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)    #unique=True
    description = db.Column(db.String(320), nullable=False)  #unique=True
    price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    sale = db.Column(db.Boolean, default=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)
    photos = db.relationship('Photo', back_populates='product')
    sizes = db.relationship('Size', secondary=product_size_association, back_populates='products')
    colors = db.relationship('Color', secondary=product_color_association, back_populates='products')
    # cart = db.relationship('Cart', back_populates='product')
    # ordered_items = db.relationship('OrderedItems', back_populates='product')


class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)    #unique=True
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship('Product', back_populates='photos')


class Size(db.Model):
    __tablename__ = 'sizes'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), nullable=False)    #unique=True
    products = db.relationship('Product', secondary=product_size_association, back_populates='sizes')


class Color(db.Model):
    __tablename__ = 'colors'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(50), nullable=False)    #unique=True
    products = db.relationship('Product', secondary=product_color_association, back_populates='colors')


# # Užsakymas

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    # product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    # product = db.relationship('Product', back_populates='cart')
    product_name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='cart')    #lazy=True insted of back_populates

class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(20), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)   #list of statuse
    ordered_items = db.relationship('OrderedItems', back_populates='order')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='orders')   #lazy=True insted of back_populates
    delivery_info = db.relationship('DeliveryInfo', back_populates='order', uselist=False)

class OrderedItems(db.Model):
    __tablename__ = 'ordered_items'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    # product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    # product = db.relationship('Product', back_populates='ordered_items')
    product_name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float(120), nullable=False)
    oder_no = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship('Orders', back_populates='ordered_items')   #lazy=True insted of back_populates

class DeliveryInfo(db.Model):
    __tablename__ = 'delivery_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    surname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)   #email format
    phone_no = db.Column(db.Integer, nullable=False)    #not integer
    street = db.Column(db.String(120), nullable=False)
    street_number = db.Column(db.Integer, nullable=False)
    flat_number = db.Column(db.Integer, nullable=False)  #not needed
    city = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(120), nullable=False)
    postal_code = db.Column(db.String(120), nullable=False)
    payment_method = db.Column(db.String(120), nullable=False, default='Bank transfer')
    order_no = db.Column(db.Integer, nullable=False)    #not integer
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship('Orders', back_populates='delivery_info')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='delivery_info') #lazy=True insted of back_populates


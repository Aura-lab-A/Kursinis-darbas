
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from flask_login import UserMixin
from Kursinis import app, db


# Users 
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False) #Should it be unique?
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(120), nullable=False) #Should it be nullab;e?
    #date joined?

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



# Produktai
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
    name = db.Column(db.String(120), nullable=False)    #unique=True
    description = db.Column(db.String(120), nullable=False)  #unique=True
    price = db.Column(db.Float(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(120), nullable=False)
    photos = db.relationship('Photo', back_populates='product')
    sizes = db.relationship('Size', secondary=product_size_association, back_populates='products')
    colors = db.relationship('Color', secondary=product_color_association, back_populates='products')
    #when it was added


class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)    #unique=True
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship('Product', back_populates='photos')


class Size(db.Model):
    __tablename__ = 'sizes'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(120), nullable=False)    #unique=True
    products = db.relationship('Product', secondary=product_size_association, back_populates='sizes')


class Color(db.Model):
    __tablename__ = 'colors'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(120), nullable=False)    #unique=True
    products = db.relationship('Product', secondary=product_color_association, back_populates='colors')


# Užsakymas

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.String(120), nullable=False)
    color = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # user = db.relationship('User', lazy=True)


class OrderedItems(db.Model):
    __tablename__ = 'ordered_items'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.String(120), nullable=False)
    color = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float(120), nullable=False)
    oder_no = db.Column(db.Integer, nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # user = db.relationship('User', lazy=True)

class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.Integer, nullable=False)    #not integer
    created_on = db.Column(db.DateTime, default=datetime.now, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(120), nullable=False)   #list of statuse
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # user = db.relationship('User', lazy=True)
    # payment_id?

class DeliveryInfo(db.Model):
    __tablename__ = 'delivery_info'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.Integer, nullable=False)    #not integer
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
    payment_method = db.Column(db.String(120), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # user = db.relationship('User', lazy=True)  


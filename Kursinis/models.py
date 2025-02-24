
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedSerializer as Serializer
from Kursinis import app, db


# Vartotojai 
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    date_register = db.Column(db.String(120), nullable=False)
    cart = db.relationship('Cart', back_populates='user', uselist=False)
    orders = db.relationship('Orders', back_populates='user')

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        # return s.dumps({'user_id': self.id}).decode('utf-8')
        token = s.dumps({'user_id': self.id})
        return token
    
    @staticmethod
    def verify_reset_token(token, expires_sec=180):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age = expires_sec)['user_id']
        except Exception as e:
            print(e)
            return None
        return User.query.get(user_id)


class Visitor(db.Model):
    __tablename__ = 'visitors'
    id = db.Column(db.Integer, primary_key=True)
    cookie_id = db.Column(db.String(36), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    cart = db.relationship('Cart', back_populates='visitor', uselist=False)
    orders = db.relationship('Orders', back_populates='visitor')


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
    name = db.Column(db.String(50), nullable=False, unique=True)
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
    cart = db.relationship('Cart', back_populates='product')
    ordered_items = db.relationship('OrderedItems', back_populates='product')


class Photo(db.Model):
    __tablename__ = 'photos'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)   #unique=True
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship('Product', back_populates='photos')


class Size(db.Model):
    __tablename__ = 'sizes'
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', secondary=product_size_association, back_populates='sizes')


class Color(db.Model):
    __tablename__ = 'colors'
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(50), unique=True, nullable=False)
    products = db.relationship('Product', secondary=product_color_association, back_populates='colors')



# # Užsakymas

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship('Product', back_populates='cart')
    product_name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    sale = db.Column(db.Boolean, default=False)
    added_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='cart')
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))
    visitor = db.relationship('Visitor', back_populates='cart')


class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(20), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    ordered_items = db.relationship('OrderedItems', back_populates='order')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='orders')
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'))
    visitor = db.relationship('Visitor', back_populates='orders')
    delivery_info = db.relationship('DeliveryInfo', back_populates='order', uselist=False)


class OrderedItems(db.Model):
    __tablename__ = 'ordered_items'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship('Product', back_populates='ordered_items')
    product_name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float(120), nullable=False)
    sale_price = db.Column(db.Float, nullable=False)
    sale = db.Column(db.Boolean, default=False)
    order_no = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship('Orders', back_populates='ordered_items')


class DeliveryInfo(db.Model):
    __tablename__ = 'delivery_info'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    surname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    street = db.Column(db.String(120), nullable=False)
    street_number = db.Column(db.Integer, nullable=False)
    flat_number = db.Column(db.Integer, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(120), nullable=False)
    postal_code = db.Column(db.String(120), nullable=False)
    payment_method = db.Column(db.String(120), nullable=False, default='Bank transfer')
    order_no = db.Column(db.String(120), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    order = db.relationship('Orders', back_populates='delivery_info')


class VisitorInquire(db.Model):
    __tablename__ = 'visitor_inquires'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    surname = db.Column(db.String(120))
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text)
from flask import Flask, render_template, request, Response, redirect, url_for, session, flash
import os
import app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime, timedelta



basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + \
    os.path.join(basedir, 'puslapis.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
# login_manager.login_view = 'home'
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Log in to see this page.'


# Users 
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False) #Should it be unique?
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(120), nullable=False) #Should it be nullab;e?


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

class Chart(db.Model):
    __tablename__ = 'chart'
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
    __tablename__ = 'delivery_info2'
    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.Integer, nullable=False)    #not integer
    name = db.Column(db.String(120), nullable=False)
    surname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)   #email format
    street = db.Column(db.String(120), nullable=False)
    street_number = db.Column(db.Integer, nullable=False)
    flat_number = db.Column(db.Integer, nullable=False)  #not needed
    city = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(120), nullable=False)
    postal_code = db.Column(db.String(120), nullable=False)
    payment_method = db.Column(db.String(120), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # user = db.relationship('User', lazy=True)  



class ManoModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.email == "aura.aura@gmail.com"
    
admin = Admin(app)
admin.add_view(ModelView(Product, db.session))
admin.add_view(ManoModelView(User, db.session))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

class RegisterForm(FlaskForm):
    name = StringField('Vardas', [DataRequired()])
    email = StringField('El. paštas', [DataRequired(), Email()])
    password = PasswordField('Slaptažodis', [DataRequired()])
    confirm_password = PasswordField(
        'Pakartikite slaptažodį', [DataRequired(), EqualTo('password', 'Slaptažodžiai turi sutapti')])
    submit = SubmitField('Registruotis')

    def validate_email(self, email):
        with app.app_context():
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Šis el. paštas jau yra užregistruotas.')

    def validate_name(self, name):
        with app.app_context():
            user = User.query.filter_by(name=name.data).first()
            if user:
                raise ValidationError('Šis vartotojo vardas jau yra užregistruotas.')

class LoginForm(FlaskForm):
    email = StringField('El. paštas', validators=[DataRequired(), Email()])
    password = PasswordField('Slaptažodis', validators=[DataRequired()])
    remember = BooleanField('Prisiminti')
    submit = SubmitField('Prisijungti')

# Gal ateityje galima bus panaudoti
# class ProfileUpdateForm(FlaskForm):
#     name = StringField('Vardas', [DataRequired()])
#     email = StringField('El. paštas', [DataRequired(), Email()])
#     submit = SubmitField('Atnaujinti')

class ChartForm(FlaskForm):
    product_id = IntegerField('Produkto ID', validators=[DataRequired()])
    product_name = StringField('Producto vardas', validators=[DataRequired()])
    size = StringField('Produkto dydis', validators=[DataRequired()])
    color = StringField('Produkto spalva', validators=[DataRequired()])
    quantity = IntegerField('Kiekis', validators=[DataRequired(), NumberRange(min=0)])
    price = DecimalField('Kaina', validators=[DataRequired(), NumberRange(min=0)])
    added_at = StringField('Produkto spalva', validators=[DataRequired()])    #datetime
    # user_id
    submit = SubmitField('Į krepšelį')

class OrderItemForm(FlaskForm):
    product_id = IntegerField('Produkto ID', validators=[DataRequired()])
    product_name = StringField('Producto vardas', validators=[DataRequired()])
    size = StringField('Produkto dydis', validators=[DataRequired()])
    color = StringField('Produkto spalva', validators=[DataRequired()])
    quantity = IntegerField('Kiekis', validators=[DataRequired(), NumberRange(min=0)])
    price = DecimalField('Kaina', validators=[DataRequired(), NumberRange(min=0)])
    # user_id
    submit = SubmitField('Patvirtinti prekes')

# class Orders(FlaskForm):
#     order_no = IntegerField('Užsakymo ID', validators=[DataRequired()])
#     created_on = StringField('Data', validators=[DataRequired()])     #date????
#     total_price = DecimalField('Kaina', validators=[DataRequired(), NumberRange(min=0)])
#     status = StringField('Statusas', validators=[DataRequired()])  #list of statuses
#     # user_id 
#     submit = SubmitField('Pateikti užsakymą')


class DeliveryInfoForm(FlaskForm):
    name = StringField('Vardas', validators=[DataRequired()])
    surname = StringField('Pavardė', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])    #email format
    street = StringField('Gatvė', validators=[DataRequired()])
    street_number = IntegerField('Namo numeris', validators=[DataRequired(), NumberRange(min=0)])
    flat_number = IntegerField('Buto numeris', validators=[DataRequired()]) #validators
    city = StringField('Miestas', validators=[DataRequired()])
    country = StringField('Šalis', validators=[DataRequired()])
    postal_code = StringField('Pašto kodas', validators=[DataRequired()])
    payment_method = StringField('Mokėjimo metodas', validators=[DataRequired()])
    # user_id
    submit = SubmitField('Patikti užsakymą')



@app.route('/base')
def base() -> Response:
    return render_template('base.html')

@app.route('/home')
def home() -> Response:
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registracija sėkminga! Galite prisijungti.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)          
            next_page = request.args.get('next')  #kas cia?
            return redirect(next_page) if next_page else redirect(url_for('login'))
        else:
            flash('El. paštas arba slaptažodis nėra teisingi.', 'danger')
    return render_template('login.html', form=form)

# Naujas užsakymas:
# @app.route('/new_entry', methods=['GET', 'POST'])
# @login_required
# def new_entry():
#     form = forms.EntryForm()
#     if form.validate_on_submit():
#         income_checked = request.form.get('income')
#         if income_checked:
#             new_entry = Entry(income=True,
#                           sum=form.sum.data, user_id=current_user.id)
#         else:
#             new_entry = Entry(income=False,
#                           sum=form.sum.data, user_id=current_user.id)
#         db.session.add(new_entry)
#         db.session.commit()
#         flash('Entry was created successfully', 'success')
#         return redirect(url_for('entries'))
#     return render_template('new_entry.html', form=form)

# Užsakymai:
# @app.route('/entries')
# @login_required
# def entries():
#     my_entries = Entry.query.filter_by(user_id=current_user.id).all()
#     return render_template('entries.html', all_entries=my_entries, datetime=datetime)

# Profilis
@app.route('/account')
@login_required
def account():  
    return render_template('account.html')

# @app.route('/search', methods=['POST'])
# def search():
#     query = request.form['query']
#     # Perform search and return results
#     return render_template('results.html', query=query, results=results)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# @app.route('/gaminiai')
# def gaminiai() -> Response:
#     return render_template('gaminiai.html')

@app.route('/printai')
def printai() -> Response:
    page = request.args.get('page', 1, type=int)
    all_prints = Product.query.filter(Product.category =='print').paginate(page=page, per_page=6)
    print_ids = [print_item.id for print_item in all_prints.items]
    all_photos = Photo.query.filter(Photo.product_id.in_(print_ids)).all()
    return render_template('printai.html', all_prints=all_prints, all_photos=all_photos)

@app.route('/zvakes')
def zvakes() -> Response:
    return render_template('zvakes.html')

@app.route('/kazkas')
def kazkas() -> Response:
    return render_template('kazkas.html')

@app.route('/produktas/<int:product_id>', methods=['GET', 'POST'])
def produktas(product_id) -> Response:
    if request.method == 'GET':
        produktas = Product.query.get(product_id)
        max_quantity = produktas.quantity
        sizes = produktas.sizes
        colors = produktas.colors
        photos = produktas.photos
        other_products = Product.query.filter(
            Product.category == produktas.category,
            Product.id != produktas.id,
            ).limit(3)
        other_product_ids = [product.id for product in other_products]
        other_photos = Photo.query.filter(Photo.product_id.in_(other_product_ids)).all()
        return render_template('produktas.html', produktas=produktas, sizes=sizes, colors=colors, photos=photos, max_quantity=max_quantity, other_products=other_products, other_photos=other_photos)
    
    else:
    # print(request.form)
    # form = Chart()
    # if form.validate_on_submit():
        produktas = Product.query.get(product_id)
        # product_exists = Chart.query.filter_by(Chart.product_id==product_id).first()
        # if product_exists:
        #     try:
        #         product_exists.quantity = product_exists.quantity+int(request.form.get("quantity"))
        #         db.session.commit()
        #         flash(f'{product_exists.product_name} kiekis buvo atnaujintas.')
        #     except Exception as e:
        #         flash(f'{product_exists.product_name} kiekis nebuvo atnaujintas.')
        item_in_chart = Chart(
            product_id = produktas.id,
            product_name = produktas.name,
            size = request.form.get("size"),
            color = request.form.get("color"),
            quantity = int(request.form.get("quantity")),
            price = produktas.price,
            added_at = datetime.now()
            # user
            )
        produktas.quantity -= item_in_chart.quantity     #here or when placing order?
        db.session.add(item_in_chart)
        db.session.commit()
        flash('Produktas perkeltas į krepšelį!', 'success')
        return redirect(url_for('produktas', product_id = product_id))    #peržiūrėti


# def updated_chart():
#     now = datetime.now()
#     time_span = timedelta(minutes=30)
#     old_items = Chart.query.filter(now > Chart.added_at+time_span).all()
#     for old_item in old_items:
#         db.session.delete(old_item)
#     db.session.commit()
#     items_in_chart = Chart.query.all()
#     return items_in_chart


# products = {product.id: product for product in Product.query.all()}
# for old_item in old_items:
#     if old_item.product_id in products:
#         products[old_item.product_id].quantity += old_item.quantity

@app.route('/delete/<int:id>')
def delete_cart_item(id):
    item_in_chart = Chart.query.get(id)      #updated_chart()
    db.session.delete(item_in_chart)
    db.session.commit()
    return redirect(url_for('chart'))

@app.route('/delete')
def delete_cart_items():
    items_in_chart = Chart.query.all()      #updated_chart()
    for item_in_chart in items_in_chart:
        db.session.delete(item_in_chart)
    db.session.commit()
    return redirect(url_for('chart'))


@app.route('/chart', methods=['GET', 'POST'])
def chart() -> Response:
    if request.method == 'GET':
        items_in_chart = Chart.query.all()      #updated_chart()
        items_in_chart_ids = [item.product_id for item in items_in_chart]
        items_in_chart_photos = Photo.query.filter(Photo.product_id.in_(items_in_chart_ids)).all()
        total_price = 0
        for item in items_in_chart:
            total_price += item.price * item.quantity
        return render_template('chart.html', items_in_chart=items_in_chart, total_price=total_price, items_in_chart_photos=items_in_chart_photos)
    else:
        oder_number = 'WTHI random number'
        items_in_chart = Chart.query.all()
        for item in items_in_chart:
            new_ordered_item = OrderedItems(
                product_id = item.product_id,
                product_name = item.product_name,
                size = item.size,
                color = item.color,
                quantity = int(item.quantity),
                price = item.price,
                oder_no = oder_number
                # user
                )
            db.session.add(new_ordered_item)
            db.session.commit()    #not needed

        new_order = Orders(
            order_no = oder_number,
            created_on = datetime.now(),
            total_price = total_price,
            status = 'status',
            # user_id 
            )
        db.session.add(new_order)
        db.session.commit()
        flash('Užsakymas rezervuotas!', 'success')
        return redirect(url_for('delivery', new_order=new_order, order_id=new_order.id))


@app.route('/delivery/<int:order_id>', methods=['GET', 'POST'])
def delivery(order_id) -> Response:
    order = Orders.query.get(order_id)
    form = DeliveryInfoForm()
    if form.validate_on_submit():
        delivery_info = DeliveryInfo(
            order_no = order.order_no,
            name=form.name.data,
            surname=form.surname.data,             
            email=form.email.data,
            street=form.street.data,
            street_number=form.street_number.data,
            flat_number=form.flat_number.data,
            city=form.city.data,
            country=form.country.data,
            postal_code=form.postal_code.data,
            payment_method=form.payment_method.data
            #user
            )
        db.session.add(delivery_info)

        chart_items = Chart.query.all()
        for chart_item in chart_items:
            db.session.delete(chart_item)

        db.session.commit()
        flash('Užsakymas pateiktas sėkmingai!', 'success')
        return redirect(url_for('oder_info', delivery_info=delivery_info, order=order, order_id=order_id))
    return render_template('delivery.html', form=form, order_id=order_id)


@app.route('/oder_info/<int:order_id>')
def oder_info(order_id) -> Response:
    order = Orders.query.get(order_id)
    return render_template('order_info.html', order=order)




@app.route('/apie_mus')
def apie_mus() -> Response:
    return render_template('apie_mus.html')


if __name__ == '__main__':
    app.run(debug=True)
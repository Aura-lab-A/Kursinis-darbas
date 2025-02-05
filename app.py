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


class OrderItemForm(FlaskForm):
    product_id = IntegerField('Produkto ID', validators=[DataRequired()])
    product_name = StringField('Producto vardas', validators=[DataRequired()])
    size = StringField('Produkto dydis', validators=[DataRequired()])
    color = StringField('Produkto spalva', validators=[DataRequired()])
    quantity = IntegerField('Kiekis', validators=[DataRequired(), NumberRange(min=0)])
    price = DecimalField('Kaina', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Į krepšelį')




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
        sizes = Size.query.filter(Size.products.any(id=product_id)).all()
        colors = Color.query.filter(Color.products.any(id=product_id)).all()
        photos = Photo.query.filter(Photo.product_id == product_id).all()
        all_prints = Product.query.filter(Product.category =='print').all()
        print_ids = [print.id for print in all_prints]
        all_photos = Photo.query.filter(Photo.product_id.in_(print_ids)).all()
        return render_template('produktas.html', produktas=produktas, sizes=sizes, colors=colors, photos=photos, max_quantity=max_quantity, all_prints=all_prints, all_photos=all_photos)
    
    else:
        print(request.form)
    # form = OrderItemForm()
    # if form.validate_on_submit():
        produktas = Product.query.get(product_id)
        new_ordered_item = OrderedItems(
            product_id = produktas.id,
            product_name = produktas.name,
            size = request.form.get("size"),
            color = request.form.get("color"),
            quantity = int(request.form.get("quantity")),
            price = produktas.price,
            oder_no = 'random generator'
            )
        db.session.add(new_ordered_item)
        db.session.commit()
        flash('Produktas perkeltas į krepšelį!', 'success')
        return redirect(url_for('produktas', product_id = product_id))



@app.route('/chart')
def chart() -> Response:
    return render_template('chart.html')

@app.route('/apie_mus')
def apie_mus() -> Response:
    return render_template('apie_mus.html')


if __name__ == '__main__':
    app.run(debug=True)
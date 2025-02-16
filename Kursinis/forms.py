
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange
from flask_wtf.file import FileField, FileRequired
from datetime import datetime, timedelta
from Kursinis import User, Product, current_user




class RegisterForm(FlaskForm):
    name = StringField('Vardas', [DataRequired()])
    email = StringField('El. paštas', [DataRequired(), Email()])
    password = PasswordField('Slaptažodis', [DataRequired()])
    confirm_password = PasswordField(
        'Pakartikite slaptažodį', [DataRequired(), EqualTo('password', 'Slaptažodžiai turi sutapti')])
    submit = SubmitField('Registruotis')

    def validate_email(self, email):
        # with app.app_context():
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Šis el. paštas jau yra užregistruotas.')

    def validate_name(self, name):
        # with app.app_context():
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

# class PaskyrosAtnaujinimoForma(FlaskForm):
#     vardas = StringField('Vardas', [DataRequired()])
#     el_pastas = StringField('El. paštas', [DataRequired()])
#     nuotrauka = FileField('Atnaujinti profilio nuotrauką', validators=[FileAllowed(['jpg', 'png'])])
#     submit = SubmitField('Atnaujinti')

#     def tikrinti_varda(self, vardas):
#         if vardas.data != current_user.vardas:
#             vartotojas = Vartotojas.query.filter_by(vardas=vardas.data).first()
#             if vartotojas:
#                 raise ValidationError('Šis vardas panaudotas. Pasirinkite kitą.')

#     def tikrinti_pasta(self, el_pastas):
#         if el_pastas.data != current_user.el_pastas:
#             vartotojas = Vartotojas.query.filter_by(el_pastas=el_pastas.data).first()
#             if vartotojas:
#                 raise ValidationError('Šis el. pašto adresas panaudotas. Pasirinkite kitą.')

# class UzklausosAtnaujinimoForma(FlaskForm):
#     el_pastas = StringField('El. paštas', validators=[DataRequired(), Email()])
#     submit = SubmitField('Gauti')

#     def validate_email(self, el_pastas):
#         user = Vartotojas.query.filter_by(el_pastas=el_pastas.data).first()
#         if user is None:
#             raise ValidationError('Nėra paskyros, registruotos šiuo el. pašto adresu. Registruokitės.')


# class SlaptazodzioAtnaujinimoForma(FlaskForm):
#     slaptazodis = PasswordField('Slaptažodis', validators=[DataRequired()])
#     patvirtintas_slaptazodis = PasswordField('Pakartokite slaptažodį',
#                                              validators=[DataRequired(), EqualTo('slaptazodis')])
#     submit = SubmitField('Atnaujinti Slaptažodį')




class CartForm(FlaskForm):
    product_id = IntegerField('Produkto ID', validators=[DataRequired()])
    product_name = StringField('Produkto vardas', validators=[DataRequired()])
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
    phone_no = IntegerField('Telefono numeris', validators=[DataRequired(), NumberRange(min=0)])     #validators
    street = StringField('Gatvė', validators=[DataRequired()])
    street_number = IntegerField('Namo numeris', validators=[DataRequired(), NumberRange(min=0)])
    flat_number = IntegerField('Buto numeris', validators=[DataRequired()]) #validators
    city = StringField('Miestas', validators=[DataRequired()])
    country = StringField('Šalis', validators=[DataRequired()])
    postal_code = StringField('Pašto kodas', validators=[DataRequired()])
    payment_method = StringField('Mokėjimo metodas', validators=[DataRequired()])
    # user_id
    submit = SubmitField('Patikti užsakymą')


class ShopItemsForm(FlaskForm):
    producy_name = StringField('Produkto vardas', validators=[DataRequired()])
    description = StringField('Produkto aprašymas', validators=[DataRequired()])
    price = DecimalField('Vieneto kaina', validators=[DataRequired(), NumberRange(min=0)])   #Float
    quantity = IntegerField('Kiekis', validators=[DataRequired(), NumberRange(min=0)])
    category = StringField('Produkto kategorija', validators=[DataRequired()])
    # photos = FileField('Produkto nuotrauka', validators=[FileRequired()])
    # sizes = db.relationship('Size', secondary=product_size_association, back_populates='products')
    # colors = db.relationship('Color', secondary=product_color_association, back_populates='products')
    add_product = SubmitField('Pridėti produktą')
    update_product = SubmitField('Atnaujinti produktą')


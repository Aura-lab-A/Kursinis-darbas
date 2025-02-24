
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, IntegerField, DecimalField, EmailField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, NumberRange, Optional, Regexp
from flask_wtf.file import FileField, FileRequired, FileAllowed
from Kursinis import User, Product, current_user, app




class RegisterForm(FlaskForm):
    name = StringField('Vardas', [DataRequired()])
    email = EmailField('El. paštas', [DataRequired(), Email()])
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
    email = EmailField('El. paštas', validators=[DataRequired(), Email()])
    password = PasswordField('Slaptažodis', validators=[DataRequired()])
    remember = BooleanField('Prisiminti')
    submit = SubmitField('Prisijungti')


class AccountUpdateForm(FlaskForm):
    name = StringField('Vardas', [DataRequired()])
    email = StringField('El. paštas', [DataRequired(), Email()])
    submit = SubmitField('Atnaujinti')

    def validate_name(self, name):
        if name.data != current_user.name:
            user = User.query.filter_by(name=name.data).first()
            if user:
                raise ValidationError('Šis vardas panaudotas. Pasirinkite kitą.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Šis el. pašto adresas panaudotas. Pasirinkite kitą.')


class ResetRequestForm(FlaskForm):
    email = StringField('El. paštas', validators=[DataRequired(), Email()])
    submit = SubmitField('Gauti')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Nėra paskyros, registruotos šiuo el. pašto adresu. Registruokitės.')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Slaptažodis', validators=[DataRequired()])
    confirm_password = PasswordField('Pakartokite slaptažodį', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Atnaujinti slaptažodį')


class ContactForm(FlaskForm):
    name = StringField('Vardas*', [DataRequired()])
    surname = StringField('Pavardė', [Optional()])
    email = StringField('El. paštas*', [DataRequired(), Email()])
    message = StringField('Žinutė*', [DataRequired()])
    submit = SubmitField('Siųsti')


class ShopItemsForm(FlaskForm):
    name = StringField('Produkto vardas', validators=[DataRequired()])
    description = StringField('Produkto aprašymas', validators=[DataRequired()])
    price = FloatField('Kaina', validators=[DataRequired()])
    sale_price = FloatField('Išpardavimo kaina', validators=[DataRequired()])
    sale = BooleanField('Išpardavimas')
    quantity = IntegerField('Kiekis', validators=[DataRequired(), NumberRange(min=0)])
    category = StringField('Produkto kategorija', validators=[DataRequired()])
    add_product = SubmitField('Pridėti produktą')
    update_product = SubmitField('Atnaujinti produktą')


class AddPhotoForm(FlaskForm):
    photo1 = FileField('Pridėti nuotrauką #1', validators=[FileAllowed(['jpg', 'png'])])
    photo2 = FileField('Pridėti nuotrauką #2', validators=[FileAllowed(['jpg', 'png'])])
    photo3 = FileField('Pridėti nuotrauką #3', validators=[FileAllowed(['jpg', 'png'])])
    add_photo = SubmitField('Pridėti')


class DeliveryInfoForm(FlaskForm):
    name = StringField('Vardas', validators=[DataRequired()])
    surname = StringField('Pavardė', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_no = IntegerField('Telefono numeris', validators=[DataRequired()])    # Regexp(r'^\+?\d{9,15}$', message="Netinkamas telefono numerio formatas.")
    street = StringField('Gatvė', validators=[DataRequired()])
    street_number = IntegerField('Namo numeris', validators=[DataRequired(), NumberRange(min=1)])
    flat_number = IntegerField('Buto numeris', validators=[Optional(), NumberRange(min=1)])
    city = StringField('Miestas', validators=[DataRequired()])
    country = StringField('Šalis', validators=[DataRequired()])
    postal_code = StringField('Pašto kodas', validators=[DataRequired()])
    payment_method = StringField('Mokėjimo metodas', validators=[DataRequired()])
    submit = SubmitField('Pateikti užsakymą')





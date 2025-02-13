import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user
# from flask_mail import Mail
# from biudzetas.email_settings import *


basedir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + \
    os.path.join(basedir, 'puslapis.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
# db.create_all()
with app.app_context():
    db.create_all()


from Kursinis.models import User, Product
from Kursinis.models import *

bcrypt = Bcrypt(app)
# mail = Mail(app)

login_manager = LoginManager(app)
# login_manager.login_view = 'home'
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Log in to see this page.'


@login_manager.user_loader
def load_user(user_id):
    db.create_all()
    return User.query.get(int(user_id))

class ManoModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.email == "admin@gmail.com"

from Kursinis import routes
admin = Admin(app)
admin.add_view(ManoModelView(User, db.session))
admin.add_view(ModelView(Product, db.session))

# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = MAIL_USERNAME
# app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
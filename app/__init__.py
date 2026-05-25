import os

from flask import Flask
from flask_mail import Mail

from app.models import db


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
	__name__,
	template_folder=os.path.join(BASE_DIR, '..', 'templates'),
	static_folder=os.path.join(BASE_DIR, '..', 'static'),
)

app.config['SECRET_KEY'] = 'abc'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, '..', 'data', '99dev.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = '99desenvolvedores@gmail.com'
app.config['MAIL_PASSWORD'] = 'lser rczm dpvo wzhf'
app.config['MAIL_DEFAULT_SENDER'] = '99desenvolvedores@gmail.com'

db.init_app(app)

mail = Mail(app)
import os

from flask import Flask
from flask_mail import Mail

from app.models import db

from itsdangerous import URLSafeTimedSerializer

from authlib.integrations.flask_client import OAuth

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
	__name__,
	template_folder=os.path.join(BASE_DIR, '..', 'templates'),
	static_folder=os.path.join(BASE_DIR, '..', 'static'),
)

load_dotenv(os.path.join(BASE_DIR, '..', '.env'))

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Inicializa e configura o OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, '..', 'data', '99dev.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOADS_PRIVADOS_DIR'] = os.path.join(BASE_DIR, '..', 'uploads_privados', 'entregas')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = '99desenvolvedores@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = '99desenvolvedores@gmail.com'

db.init_app(app)

mail = Mail(app)
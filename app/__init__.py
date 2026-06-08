import os

from flask import Flask
from flask_mail import Mail

from app.models import db

from itsdangerous import URLSafeTimedSerializer

from authlib.integrations.flask_client import OAuth


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
	__name__,
	template_folder=os.path.join(BASE_DIR, '..', 'templates'),
	static_folder=os.path.join(BASE_DIR, '..', 'static'),
)

# colocar em variáveis de ambiente depois
app.config['SECRET_KEY'] = 'IFPB-99Dev'
app.config['GOOGLE_CLIENT_ID'] = '897300149640-echvsi28po2utgc31ai3gso1odiqivn6.apps.googleusercontent.com'
app.config['GOOGLE_CLIENT_SECRET'] = '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'

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

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = '99desenvolvedores@gmail.com'
app.config['MAIL_PASSWORD'] = 'lser rczm dpvo wzhf'
app.config['MAIL_DEFAULT_SENDER'] = '99desenvolvedores@gmail.com'

db.init_app(app)

mail = Mail(app)
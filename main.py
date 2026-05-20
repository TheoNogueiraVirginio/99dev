from flask import Flask,render_template, request, redirect

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import input_required, Email

#importando a função de cadastro do usuário
from app.functions import cadastrar_usuario

import os
from app.models import db, Usuario

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', '99dev.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


## extremamente provisório, só pra testar o formulário de cadastro, depois a gente tira isso daqui
app.config['SECRET_KEY'] = 'abc'

## formulário de cadastro
class CadastroForm(FlaskForm):
    email = StringField('Email', validators=[Email(message="Email inválido")])
    senha = PasswordField('senha', validators=[input_required()])
    dev = BooleanField('Eu sou um dev')
    pessoa = BooleanField('Eu preciso de um dev')

# rota provisoria
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroForm()
    
    #cadastro valido
    if form.validate_on_submit():
        
        if form.dev.data:
            cargo_definido = 'dev'
        else:
            cargo_definido = 'cliente'
            
        novo_usuario = Usuario(
            email=form.email.data,
            senha=form.senha.data, 
            cargo=cargo_definido
        )
        
        db.session.add(novo_usuario)
        db.session.commit()
        
    return render_template('cadastro.html', form=form)

@app.route('/login')
def login():
    return render_template('login.html')


# executa a aplicação
if __name__ == '__main__':
    app.run(debug=True, port=3001)
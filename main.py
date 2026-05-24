import os

from flask import Flask, flash, render_template, redirect

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import input_required, Email

#importando a função de cadastro do usuário
from app.functions import cadastrar_usuario
from app.models import db

app = Flask(__name__)

## extremamente provisório, só pra testar o formulário de cadastro, depois a gente tira isso daqui
app.config['SECRET_KEY'] = 'abc'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', '99dev.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

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
            
        #envia payload para a função de cadastro do usuário
        try:
            cadastrar_usuario(
                email=form.email.data,
                senha=form.senha.data,
                cargo_definido=cargo_definido
            )
        except Exception as e:
            flash(f"Falha ao cadastrar usuário: {str(e)}", "error")
            return render_template('cadastro.html', form=form, error=str(e))
        
        return redirect('/login')
        
    return render_template('cadastro.html', form=form)

@app.route('/login')
def login():
    return render_template('login.html')


# executa a aplicação
if __name__ == '__main__':
    app.run(debug=True, port=3001)
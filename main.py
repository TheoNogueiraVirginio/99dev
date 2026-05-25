import os

from flask import Flask, flash, render_template, redirect

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import input_required, Email

#importando a função de cadastro do usuário
from app.functions import cadastrar_usuario
from app.models import db

from flask_mail import Mail, Message

app = Flask(__name__)


app.config['SECRET_KEY'] = 'abc'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'data', '99dev.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de email para recuperação de senha
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
# Email e senha do 99
app.config['MAIL_USERNAME'] = '99desenvolvedores@gmail.com'
app.config['MAIL_PASSWORD'] = 'lser rczm dpvo wzhf'

mail = Mail(app)

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

#rota para a página de recuperação de senha
@app.route('/recuperar-senha')
def recuperar_senha():
    return render_template('recuperar-senha.html')

@app.route('/enviar-instrucoes')
def enviar_instrucoes():
    try:
        msg = Message(
            subject="Instruções para Recuperação de Senha - 99Dev",
            recipients=[""] # lógica para obter o email do user
        )

        msg.body = "recuperar senha"
        mail.send(msg)

        return "email enviado com sucesso"
    except Exception as e:
        return f"Falha ao enviar email: {str(e)}"
    
    
# executa a aplicação
if __name__ == '__main__':
    app.run(debug=True, port=3001)
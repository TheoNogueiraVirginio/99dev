from flask import Flask,render_template, request, redirect

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import input_required, Email

#importando a função de cadastro do usuário
from app.functions import cadastrar_usuario

app = Flask(__name__)

## extremamente provisório, só pra testar o formulário de cadastro, depois a gente tira isso daqui
app.config['SECRET_KEY'] = 'abc'

## formulário de cadastro
class CadastroForm(FlaskForm):
    email = StringField('Email', validators=[Email(message="Email inválido")])
    senha = PasswordField('senha', validators=[input_required()])
    dev = BooleanField('I\'m a dev')
    pessoa = BooleanField('I need a dev')

# rota provisoria
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroForm()
    
    #cadastro valido
    if form.validate_on_submit():
        cadastrar_usuario(form.email.data, form.senha.data)
        return redirect('/login')
    
    return render_template('cadastro.html', form=form)

@app.route('/login')
def login():
    return render_template('login.html')


# executa a aplicação
if __name__ == '__main__':
    app.run(debug=True, port=3001)
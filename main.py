from flask import flash, render_template, redirect

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import input_required, Email

#importando a função de cadastro do usuário
from app import app, db
from app.functions import cadastrar_usuario, solicitar_recuperacao_senha

with app.app_context():
    db.create_all()

## formulário de cadastro
class CadastroForm(FlaskForm):
    email = StringField('Email', validators=[Email(message="Email inválido")])
    senha = PasswordField('senha', validators=[input_required()])
    dev = BooleanField('Eu sou um dev')
    pessoa = BooleanField('Eu preciso de um dev')

class RecuperarSenhaForm(FlaskForm):
    email = StringField('Email', validators=[Email(message="Email inválido")])

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
@app.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    form = RecuperarSenhaForm()
    if form.validate_on_submit():
        try:
            solicitar_recuperacao_senha(form.email.data)
            flash("Instruções para recuperação de senha enviadas para seu email", "success")
        except Exception as e:
            flash(f"Falha ao enviar email: {str(e)}", "error")
    return render_template('recuperar-senha.html', form=form)
 
    
# executa a aplicação
if __name__ == '__main__':
    app.run(debug=True, port=3001)
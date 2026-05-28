from flask import flash, render_template, redirect, session

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import input_required, Email

#importando a função de cadastro do usuário
from app import app, db
from app.functions import atualizar_senha, cadastrar_usuario, autenticar_usuario, solicitar_recuperacao_senha, validar_token

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

class NovaSenhaForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[input_required()])
    password_confirm = PasswordField('Confirme a Nova Senha', validators=[input_required()])

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

@app.route('/login', methods=["GET","POST"])
def login():
    form = CadastroForm()

    if form.validate_on_submit():
        try:
            usuario = autenticar_usuario(form.email.data, form.senha.data)

            session["id_usuario"] = usuario.id
            flash("Login realizado com sucesso!", "success")
            return redirect('/home')

        except ValueError as e:
            flash(str(e), "error")

    return render_template('login.html', form=form)

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
 
#rota nova senha botar token de recuperação de senha depois
@app.route('/nova-senha/<token>', methods=['GET', 'POST'])
def nova_senha(token):
    form = NovaSenhaForm()
    if form.validate_on_submit():
        
        if form.password.data != form.password_confirm.data:
            flash("As senhas não coincidem", "error")
            return render_template('nova-senha.html', form=form)
        
        email = validar_token(token)
        if not email:
            flash("Token inválido ou expirado", "error")
            return redirect('/recuperar-senha')

        atualizar_senha(email=email, nova_senha=form.password.data)
        flash("Senha atualizada com sucesso", "success")
        return redirect('/login')

    return render_template('nova-senha.html', form=form)


# executa a aplicação
if __name__ == '__main__':
    app.run(debug=True, port=3001)
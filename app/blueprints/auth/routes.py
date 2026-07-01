from flask import Blueprint, flash, render_template, redirect, request, session, url_for

from app import app, google
from app.models import Desenvolvedor
from app.forms import CadastroForm, RecuperarSenhaForm, NovaSenhaForm
from app.functions import (
    cadastrar_usuario, autenticar_usuario, gerenciar_login_google,
    solicitar_recuperacao_senha, validar_token, atualizar_senha,
)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/")
def home():
    return render_template('home.html')


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroForm()
    if form.validate_on_submit():
        cargo_definido = 'dev' if form.dev.data else 'cliente'
        try:
            cadastrar_usuario(email=form.email.data, senha=form.senha.data, cargo=cargo_definido)
        except Exception as e:
            flash(f"Falha ao cadastrar usuário: {str(e)}", "error")
            return render_template('cadastro.html', form=form, error=str(e))
        return redirect('/login')
    return render_template('cadastro.html', form=form)


@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    form = CadastroForm()
    if form.validate_on_submit():
        try:
            usuario = autenticar_usuario(form.email.data, form.senha.data)
            session["id_usuario"] = usuario.id
            session["tipo_usuario"] = "dev" if isinstance(usuario, Desenvolvedor) else "cliente"
            flash("Login realizado com sucesso!", "success")
            if session["tipo_usuario"] == 'dev':
                return redirect('/DashboardDev')
            return redirect('/dashboard')
        except ValueError as e:
            flash(str(e), "error")
    return render_template('login.html', form=form)


@auth_bp.route('/login/google')
def login_google():
    session['cargo_pretendido'] = request.args.get('cargo', 'cliente')
    redirect_uri = url_for('auth.authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route('/authorize/google')
def authorize_google():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        email = user_info['email']
        cargo_escolhido = session.pop('cargo_pretendido', 'cliente')
        usuario = gerenciar_login_google(email, cargo_escolhido)
        session["id_usuario"] = usuario.id
        session["tipo_usuario"] = "dev" if isinstance(usuario, Desenvolvedor) else "cliente"
        flash("Login com Google realizado com sucesso!", "success")
        if session["tipo_usuario"] == "dev":
            return redirect("/DashboardDev")
        return redirect("/dashboard")
    except Exception:
        flash("Ocorreu um erro ao tentar fazer login com o Google.", "error")
        return redirect('/login')


@auth_bp.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    form = RecuperarSenhaForm()
    if form.validate_on_submit():
        try:
            solicitar_recuperacao_senha(form.email.data)
            flash("Instruções para recuperação de senha enviadas para seu email", "success")
        except Exception as e:
            flash(f"Falha ao enviar email: {str(e)}", "error")
    return render_template('recuperar-senha.html', form=form)


@auth_bp.route('/nova-senha/<token>', methods=['GET', 'POST'])
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


@auth_bp.route("/logout", methods=['GET'])
def sairLogin():
    session.clear()
    flash('Você saiu da sua conta, logue novamente!')
    return redirect('/login')

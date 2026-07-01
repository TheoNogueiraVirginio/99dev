from flask import Blueprint, flash, render_template, redirect, session, abort

from app.models import Cliente, Desenvolvedor
from app.forms import SuporteForm, SuporteDevForm
from app.functions import salvar_mensagem_suporte, salvar_mensagem_suporte_dev
from app.decorators import login_required

suporte_bp = Blueprint('suporte', __name__)


@suporte_bp.route('/suporte', methods=['GET', 'POST'])
@login_required
def suporte():
    form = SuporteForm()
    id_usuario = session.get("id_usuario")
    tipo_usuario = session.get("tipo_usuario")
    usuario = Desenvolvedor.query.get(id_usuario) if tipo_usuario == 'dev' else Cliente.query.get(id_usuario)
    foto_perfil = usuario.foto_perfil if usuario else None
    if form.validate_on_submit():
        try:
            salvar_mensagem_suporte(id_usuario=id_usuario, tipo_usuario=tipo_usuario,
                                    assunto=form.assunto.data, mensagem=form.mensagem.data)
            flash("Sua mensagem foi enviada com sucesso à equipe de suporte!", "success")
            return redirect('/suporte')
        except Exception as e:
            flash(f"Ocorreu um erro ao tentar registrar sua mensagem: {str(e)}", "error")
    return render_template('suporte.html', form=form, foto_perfil=foto_perfil, usuario=usuario)


@suporte_bp.route('/suporte-dev', methods=['GET', 'POST'])
@login_required
def suporteDev():
    if session.get("tipo_usuario") != "dev":
        abort(403)
    form = SuporteDevForm()
    id_dev = session["id_usuario"]
    usuario = Desenvolvedor.query.get(id_dev)
    foto_perfil = usuario.foto_perfil if usuario else None
    if form.validate_on_submit():
        try:
            salvar_mensagem_suporte_dev(id_dev=id_dev, assunto=form.assunto.data,
                                        mensagem=form.mensagem.data)
            flash("Ticket de suporte enviado com sucesso!", "success")
            return redirect('/suporte-dev')
        except Exception as e:
            flash(f"Ocorreu um erro ao enviar sua solicitação: {str(e)}", "error")
    return render_template('suporteDev.html', form=form, usuario=usuario, foto_perfil=foto_perfil)

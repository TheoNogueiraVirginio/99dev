from flask import Blueprint, flash, render_template, redirect, request, session, abort

from app.models import Cliente, Desenvolvedor
from app.forms import EditarPerfilForm, EditarDevForm
from app.functions import atualizar_perfil_cliente, atualizar_perfil_dev
from app.decorators import login_required

perfil_bp = Blueprint('perfil', __name__)


@perfil_bp.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    id_usuario = session.get("id_usuario")
    usuario = Cliente.query.get(id_usuario)
    if not usuario:
        flash("Usuário não encontrado.", "error")
        return redirect('/login')
    if session.get("tipo_usuario") == 'dev':
        abort(403)
    form = EditarPerfilForm()
    if form.validate_on_submit():
        try:
            atualizar_perfil_cliente(id_cliente=id_usuario, novo_email=form.email.data,
                                     nova_senha=form.nova_senha.data,
                                     nova_descricao=form.descricao.data,
                                     arquivo_foto=form.foto.data)
            flash("Perfil atualizado com sucesso!", "success")
            return redirect('/editar-perfil')
        except Exception as e:
            flash(str(e), "error")
    elif request.method == 'GET':
        form.email.data = usuario.email
        form.dev.data = (session.get("tipo_usuario") == 'dev')
        form.pessoa.data = (session.get("tipo_usuario") == 'cliente')
        form.descricao.data = usuario.descricao
    return render_template('perfil-editar.html', foto_perfil=usuario.foto_perfil, form=form)


@perfil_bp.route('/perfil-dev', methods=['GET', 'POST'])
@login_required
def perfildev():
    form = EditarDevForm()
    if session.get("tipo_usuario") != "dev":
        abort(403)
    usuario = Desenvolvedor.query.get(session["id_usuario"])
    if request.method == 'GET' and usuario:
        form.nome.data = usuario.nome
        form.titulo.data = usuario.titulo
        form.valor_hora.data = usuario.valor_hora
        form.skills.data = usuario.skills
        form.resumo.data = usuario.resumo
        form.github.data = usuario.github
        form.linkedin.data = usuario.linkedin
        form.exibir_dados.data = usuario.exibir_dados
    if form.validate_on_submit():
        try:
            atualizar_perfil_dev(id_dev=session["id_usuario"], nome=form.nome.data,
                                  titulo=form.titulo.data, valor_hora=form.valor_hora.data,
                                  skills=form.skills.data, resumo=form.resumo.data,
                                  github=form.github.data, linkedin=form.linkedin.data,
                                  foto_perfil=form.foto_perfil.data,
                                  foto_banner=form.foto_banner.data,
                                  novo_exibir_dados=form.exibir_dados.data)
            flash("Perfil atualizado com sucesso!", "success")
            return redirect('/perfil-dev')
        except Exception as e:
            flash(f"Erro ao atualizar perfil: {str(e)}", "error")
    return render_template('perfil.html', form=form, usuario=usuario)

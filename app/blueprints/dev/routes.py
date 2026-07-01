import os

from flask import Blueprint, flash, render_template, redirect, session, abort

from app import app, db
from app.models import Desenvolvedor, Candidatura, Entrega
from app.forms import FormularioEntregaForm
from app.functions import (
    lerDemandas, exibirSaldo, ler_candidaturas_dev, ler_pagamentos_dev,
    ler_projetos_dev, atualizar_status_por_titulo, salvar_entrega,
)
from app.decorators import login_required

dev_bp = Blueprint('dev', __name__)


@dev_bp.route("/DashboardDev", methods=['GET'])
@login_required
def dashboardDev():
    if session.get("tipo_usuario") != "dev":
        abort(403)
    id_dev = session["id_usuario"]
    usuario = Desenvolvedor.query.get(id_dev)
    demandas = lerDemandas(tipo_usuario="dev")
    saldo = exibirSaldo(id_dev)
    candidaturas = ler_candidaturas_dev(id_dev)
    foto_perfil = usuario.foto_perfil if usuario else None
    return render_template('dashboardDev.html', demandas=demandas, saldo=saldo,
                           usuario=usuario, foto_perfil=foto_perfil,
                           candidaturas=candidaturas)


@dev_bp.route('/carteira-dev', methods=['GET'])
@login_required
def carteiraDev():
    if session.get("tipo_usuario") != "dev":
        abort(403)

    id_dev = session["id_usuario"]
    usuario = Desenvolvedor.query.get(id_dev)
    pagamentos = ler_pagamentos_dev(id_dev)

    return render_template(
        'carteiraDev.html',
        usuario=usuario,
        foto_perfil=usuario.foto_perfil if usuario else None,
        pagamentos=pagamentos,
        saldo=exibirSaldo(id_dev),
    )


@dev_bp.route("/MeusProjetosDev")
@login_required
def meusProjetosDev():
    if session.get("tipo_usuario") != "dev":
        abort(403)
    id_dev = session["id_usuario"]
    usuario = Desenvolvedor.query.get(id_dev)
    projetos = ler_projetos_dev(id_dev)
    form_entrega = FormularioEntregaForm()
    entregas_por_demanda = {}
    for entrega in Entrega.query.filter_by(dev_id=id_dev).order_by(Entrega.data_envio.desc()).all():
        chave = (entrega.demanda_titulo, entrega.id_cliente)
        if chave not in entregas_por_demanda:
            entregas_por_demanda[chave] = entrega
    return render_template('Meusprojetosdev.html',
                           projetos=projetos,
                           usuario=usuario,
                           foto_perfil=usuario.foto_perfil if usuario else None,
                           form_entrega=form_entrega,
                           entregas_por_demanda=entregas_por_demanda)


@dev_bp.route("/entregar-demanda/<string:titulo>/<int:id_cliente>", methods=['POST'])
@login_required
def entregar_demanda(titulo, id_cliente):
    if session.get("tipo_usuario") != "dev":
        abort(403)

    demanda = next(
        (
            item for item in lerDemandas(tipo_usuario="cliente")
            if item.get("titulo") == titulo and str(item.get("id")) == str(id_cliente)
        ),
        None,
    )

    if not demanda or demanda.get("status") != "Em Desenvolvimento":
        flash("Esta demanda não está disponível para entrega no momento.", "error")
        return redirect('/MeusProjetosDev')

    candidatura = Candidatura.query.filter_by(
        dev_id=session["id_usuario"],
        demanda_titulo=titulo,
        id_cliente=id_cliente,
        status="aceita",
    ).first()

    if not candidatura:
        abort(403)

    form_entrega = FormularioEntregaForm()
    if not form_entrega.validate_on_submit():
        for field_errors in form_entrega.errors.values():
            for error in field_errors:
                flash(error, "error")
        return redirect('/MeusProjetosDev')

    arquivo_entrega = form_entrega.arquivo_entrega.data
    entrega_salva = None
    caminho_fisico = None

    try:
        entrega_salva = salvar_entrega(
            titulo=titulo,
            id_cliente=id_cliente,
            dev_id=session["id_usuario"],
            arquivo=arquivo_entrega,
        )
        caminho_fisico = os.path.join(app.config['UPLOADS_PRIVADOS_DIR'], entrega_salva.caminho_arquivo)
        db.session.commit()

        sucesso = atualizar_status_por_titulo(titulo, id_cliente, "Aguardando Aprovação")

        if sucesso:
            flash("Entrega da demanda enviada com sucesso! Aguarde a aprovação do cliente.", "success")
        else:
            raise RuntimeError("Não foi possível atualizar o status da demanda para Aguardando Aprovação.")

    except Exception as e:
        db.session.rollback()
        if caminho_fisico and os.path.exists(caminho_fisico):
            try:
                if entrega_salva and entrega_salva.id:
                    entrega_para_remover = Entrega.query.get(entrega_salva.id)
                    if entrega_para_remover:
                        db.session.delete(entrega_para_remover)
                        db.session.commit()
                os.remove(caminho_fisico)
            except Exception:
                db.session.rollback()
        flash(f"Falha ao processar entrega da demanda: {str(e)}", "error")

    return redirect('/DashboardDev')

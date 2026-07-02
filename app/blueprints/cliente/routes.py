from flask import Blueprint, flash, render_template, redirect, request, session, abort, url_for

from app import db
from app.models import Cliente, Desenvolvedor, Pagamento, Entrega
from app.forms import DemandaForm, AvaliacaoForm, AdicionarSaldoForm
from app.functions import (
    lerDemandas, salvarDemanda, ler_pagamentos_cliente, ler_demandas_realizadas_cliente,
    ler_candidaturas_cliente, adicionar_saldo_cliente, atualizar_status_por_titulo,
    buscar_candidatura_aceita, registrar_pagamento, validar_saldo_suficiente, salvar_avaliacao,
)
from app.decorators import login_required
from app.models import Candidatura

cliente_bp = Blueprint('cliente', __name__)


@cliente_bp.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboardCliente():
    form = DemandaForm()
    form_avaliacao = AvaliacaoForm()

    if session.get("tipo_usuario") != "cliente":
        abort(403)
    id = session["id_usuario"]
    usuario = Cliente.query.get(id)
    demandas = lerDemandas()
    pagamentos = ler_pagamentos_cliente(id)
    demandas_realizadas = ler_demandas_realizadas_cliente(id)
    candidaturas = ler_candidaturas_cliente(id)
    entregas_por_demanda = {}
    for demanda in demandas:
        if demanda.get("status") == "Aguardando Aprovação":
            entrega = Entrega.query.filter_by(
                demanda_titulo=demanda.get("titulo"),
                id_cliente=id,
            ).order_by(Entrega.id.desc()).first()
            if entrega:
                # OBS: demanda.get("id") vem do CSV como string, então a chave
                # precisa usar str(id) para bater com o "demanda.id" usado no
                # template (senão o .get() no Jinja nunca encontra a entrega).
                entregas_por_demanda[(demanda.get("titulo"), str(id))] = entrega

    if form.validate_on_submit():
        try:
            salvarDemanda(titulo=form.titulo.data, tecnologia=form.tecnologia.data,
                          descricao=form.descricao.data, orcamento=form.orcamento.data,
                          status="Aberta", id=id)
            flash("Demanda cadastrada com sucesso!", "success")
            return redirect('/dashboard')
        except Exception as e:
            flash(f"Falha ao cadastrar demanda: {str(e)}", "error")
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, "error")
    return render_template('dashboardCliente.html', form=form, demandas=demandas, form_avaliacao=form_avaliacao,
                           foto_perfil=usuario.foto_perfil if usuario else None,
                           usuario=usuario, pagamentos=pagamentos,
                           demandas_realizadas=demandas_realizadas,
                           candidaturas=candidaturas,
                           entregas_por_demanda=entregas_por_demanda)


@cliente_bp.route("/MeusProjetos", methods=['GET', 'POST'])
@login_required
def meusProjetos():
    busca = request.args.get("busca", "").strip() or None
    filtro_status = request.args.get("filtro", "").strip() or None
    demandas = lerDemandas(busca=busca, filtro_status=filtro_status)
    return render_template('MeusProjetos.html', demandas=demandas)


@cliente_bp.route('/adicionar-saldo', methods=['POST'])
@login_required
def adicionar_saldo():
    if session.get("tipo_usuario") != "cliente":
        abort(403)
    form = AdicionarSaldoForm()
    if form.validate_on_submit():
        try:
            adicionar_saldo_cliente(id_cliente=session["id_usuario"], saldo=form.valor.data)
            flash(f"Saldo de R$ {form.valor.data:.2f} adicionado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao processar o depósito: {str(e)}", "error")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, "error")
    return redirect('/carteira')


@cliente_bp.route('/carteira', methods=['GET', 'POST'])
@login_required
def carteiraCliente():
    if session.get("tipo_usuario") != "cliente":
        abort(403)
    id = session["id_usuario"]
    usuario = Cliente.query.get(id)
    form = AdicionarSaldoForm()
    pagamentos = ler_pagamentos_cliente(id)
    return render_template('carteiraCliente.html', usuario=usuario, form=form,
                           foto_perfil=usuario.foto_perfil if usuario else None,
                           pagamentos=pagamentos)


@cliente_bp.route('/demanda/<string:demanda_uuid>/pagar', methods=['POST'])
@login_required
def pagar_demanda(demanda_uuid):
    if session.get("tipo_usuario") != "cliente":
        abort(403)

    id_cliente = session["id_usuario"]
    usuario = Cliente.query.get(id_cliente)
    if not usuario:
        flash("Cliente não encontrado.", "error")
        return redirect('/login')

    demandas = lerDemandas(tipo_usuario="cliente")
    demanda = next(
        (item for item in demandas
         if item.get("uuid") == demanda_uuid and str(item.get("id")) == str(id_cliente)),
        None,
    )

    if not demanda:
        abort(404)

    if demanda.get("status") != "Concluída":
        flash("Esta demanda ainda não foi aprovada. Aprove a entrega antes de efetuar o pagamento.", "error")
        return redirect(request.referrer or url_for('cliente.dashboardCliente'))

    candidatura = buscar_candidatura_aceita(demanda_uuid)
    if not candidatura:
        flash("Não foi possível localizar o desenvolvedor responsável por esta demanda.", "error")
        return redirect(url_for('cliente.dashboardCliente'))

    if candidatura.id_cliente != id_cliente:
        flash("Não foi possível localizar o desenvolvedor responsável por esta demanda.", "error")
        return redirect(url_for('cliente.dashboardCliente'))

    dev = Desenvolvedor.query.get(candidatura.dev_id)
    if not dev:
        flash("Não foi possível localizar o desenvolvedor responsável por esta demanda.", "error")
        return redirect(url_for('cliente.dashboardCliente'))

    try:
        valor_demanda = float(str(demanda.get("orcamento", "0")).replace(',', '.'))
    except (TypeError, ValueError):
        flash("Não foi possível processar o valor desta demanda.", "error")
        return redirect(request.referrer or url_for('cliente.dashboardCliente'))

    if not validar_saldo_suficiente(usuario, valor_demanda):
        flash("Saldo insuficiente para realizar este pagamento. Adicione saldo à sua carteira.", "saldo_insuficiente")
        return redirect(request.referrer or url_for('cliente.carteiraCliente'))

    # Pagamento concluído deve reutilizar o status já existente "Fechada".
    # Assim evitamos criar um novo estado e preservamos os filtros e badges atuais do sistema.
    pagamento_confirmado = False
    try:
        usuario.saldo -= valor_demanda
        dev.saldo += valor_demanda
        registrar_pagamento(id_cliente, demanda["titulo"], valor_demanda, commit=False)
        db.session.commit()
        pagamento_confirmado = True

        if not atualizar_status_por_titulo(demanda["titulo"], id_cliente, "Fechada"):
            raise RuntimeError("Não foi possível atualizar o status da demanda para Fechada.")

        flash(f"Pagamento realizado com sucesso! R$ {valor_demanda:.2f} transferido para o desenvolvedor.", "success")
    except Exception as e:
        if pagamento_confirmado:
            try:
                cliente = Cliente.query.get(id_cliente)
                if cliente:
                    cliente.saldo += valor_demanda
                dev_compensado = Desenvolvedor.query.get(candidatura.dev_id)
                if dev_compensado:
                    dev_compensado.saldo -= valor_demanda
                pagamento = Pagamento.query.filter_by(
                    id_cliente=id_cliente,
                    titulo_demanda=demanda["titulo"],
                    valor=valor_demanda,
                ).order_by(Pagamento.id.desc()).first()
                if pagamento:
                    db.session.delete(pagamento)
                db.session.commit()
            except Exception:
                db.session.rollback()
        else:
            db.session.rollback()
        flash(f"Erro ao processar o pagamento: {str(e)}", "error")

    return redirect(request.referrer or url_for('cliente.dashboardCliente'))


@cliente_bp.route("/aprovar-demanda/<string:titulo>/<int:id_cliente>", methods=['POST'])
@login_required
def aprovar_demanda(titulo, id_cliente):
    if session.get("tipo_usuario") != "cliente":
        abort(403)

    demanda = next(
        (
            item for item in lerDemandas(tipo_usuario="cliente")
            if item.get("titulo") == titulo and str(item.get("id")) == str(id_cliente)
        ),
        None,
    )

    if not demanda or str(session.get("id_usuario")) != str(id_cliente) or demanda.get("status") != "Aguardando Aprovação":
        flash("Esta demanda não está disponível para aprovação.", "error")
        return redirect('/dashboard')

    try:
        sucesso = atualizar_status_por_titulo(titulo, id_cliente, "Concluída")

        if sucesso:
            flash("Entrega aprovada! Finalize o pagamento ao desenvolvedor abaixo.", "success")
            # Leva o cliente direto para o modal de pagamento dessa demanda,
            # em vez de simplesmente cair no dashboard sem nenhuma ação seguinte.
            return redirect(f"/dashboard#pagamento-{demanda.get('uuid')}")
        else:
            flash("Esta demanda não está disponível para aprovação.", "error")

    except Exception as e:
        db.session.rollback()
        flash(f"Falha ao processar aprovação da demanda: {str(e)}", "error")

    return redirect('/dashboard')


@cliente_bp.route("/negar-demanda/<string:titulo>/<int:id_cliente>", methods=['POST'])
@login_required
def negar_demanda(titulo, id_cliente):
    if session.get("tipo_usuario") != "cliente":
        abort(403)

    try:
        sucesso = atualizar_status_por_titulo(titulo, id_cliente, "Em Andamento")
        if sucesso:
            flash("Entrega recusada. O projeto retornou para o status Em Andamento para correções.", "success")
        else:
            flash("Erro: Não foi possível localizar a demanda indicada.", "error")
    except Exception as e:
        flash(f"Falha ao processar recusa da entrega: {str(e)}", "error")

    return redirect('/dashboard')


@cliente_bp.route("/avaliar-dev/<string:titulo>/<int:id_cliente>", methods=['POST'])
@login_required
def avaliar_dev(titulo, id_cliente):
    form = AvaliacaoForm()
    if session.get("tipo_usuario") != "cliente":
        abort(403)

    candidatura = Candidatura.query.filter_by(
        demanda_titulo=titulo,
        id_cliente=id_cliente,
        status="Aceita"
    ).first()

    if form.validate_on_submit() and candidatura:
        try:
            salvar_avaliacao(titulo, session["id_usuario"], "cliente", candidatura.dev_id, form.nota.data, form.comentario.data)
            flash("Avaliação do desenvolvedor registrada com sucesso!", "success")
        except Exception:
            flash("Erro ao salvar avaliação.", "error")

    return redirect('/dashboard')

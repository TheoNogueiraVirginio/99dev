from flask import Blueprint, flash, redirect, request, session, abort, jsonify

from app import db
from app.models import Candidatura
from app.functions import candidatar_dev, enviar_mensagem_chat, atualizar_status_demanda
from app.decorators import login_required

candidatura_bp = Blueprint('candidatura', __name__)


@candidatura_bp.route('/candidatar', methods=['POST'])
@login_required
def candidatar():
    if session.get("tipo_usuario") != "dev":
        abort(403)

    dev_id = session["id_usuario"]
    demanda_uuid = request.form.get("demanda_uuid", "").strip()
    demanda_titulo = request.form.get("demanda_titulo", "").strip()
    id_cliente = request.form.get("id_cliente", "").strip()
    proposta = request.form.get("proposta", "").strip()

    if not demanda_uuid or not demanda_titulo or not id_cliente:
        flash("Dados da demanda inválidos.", "error")
        return redirect('/DashboardDev')

    try:
        candidatura = candidatar_dev(
            dev_id=dev_id,
            demanda_uuid=demanda_uuid,
            demanda_titulo=demanda_titulo,
            id_cliente=int(id_cliente),
            proposta=proposta,
        )
        flash("Candidatura enviada! Agora você pode conversar com o cliente.", "success")
        return redirect(f'/chat/{candidatura.id}')
    except ValueError as e:
        flash(str(e), "error")
        return redirect('/DashboardDev')


@candidatura_bp.route('/candidatura/<int:candidatura_id>/aceitar', methods=['POST'])
@login_required
def aceitar_candidatura(candidatura_id):
    if session.get("tipo_usuario") != "cliente":
        return jsonify({"error": "Apenas clientes podem aceitar propostas."}), 403

    candidatura = Candidatura.query.get_or_404(candidatura_id)
    if candidatura.id_cliente != session["id_usuario"]:
        return jsonify({"error": "Sem permissão."}), 403

    if candidatura.status != 'pendente':
        return jsonify({"error": "Esta candidatura não está mais pendente."}), 400

    candidatura.status = 'aceita'
    db.session.commit()
    atualizar_status_demanda(candidatura.demanda_uuid, 'Em Desenvolvimento')
    enviar_mensagem_chat(candidatura_id, session["id_usuario"], 'cliente',
                         '✅ Proposta aceita! O projeto agora está em desenvolvimento.')
    return jsonify({"ok": True, "status": "aceita"})

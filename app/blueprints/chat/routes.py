from flask import Blueprint, render_template, request, session, abort, jsonify

from app.models import Candidatura, Desenvolvedor, Cliente
from app.functions import enviar_mensagem_chat, ler_mensagens_chat
from app.decorators import login_required

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat/<int:candidatura_id>')
@login_required
def chat(candidatura_id):
    candidatura = Candidatura.query.get_or_404(candidatura_id)
    id_usuario = session["id_usuario"]
    tipo = session["tipo_usuario"]

    if tipo == "dev" and candidatura.dev_id != id_usuario:
        abort(403)
    if tipo == "cliente" and candidatura.id_cliente != id_usuario:
        abort(403)

    dev = Desenvolvedor.query.get(candidatura.dev_id)
    cliente = Cliente.query.get(candidatura.id_cliente)
    mensagens = ler_mensagens_chat(candidatura_id)

    return render_template('chat.html',
                           candidatura=candidatura,
                           dev=dev,
                           cliente=cliente,
                           mensagens=mensagens,
                           tipo_usuario=tipo,
                           id_usuario=id_usuario)


@chat_bp.route('/chat/<int:candidatura_id>/enviar', methods=['POST'])
@login_required
def enviar_mensagem(candidatura_id):
    candidatura = Candidatura.query.get_or_404(candidatura_id)
    id_usuario = session["id_usuario"]
    tipo = session["tipo_usuario"]

    if tipo == "dev" and candidatura.dev_id != id_usuario:
        abort(403)
    if tipo == "cliente" and candidatura.id_cliente != id_usuario:
        abort(403)

    conteudo = request.json.get("conteudo", "").strip() if request.is_json else request.form.get("conteudo", "").strip()
    if not conteudo:
        return jsonify({"error": "Mensagem vazia"}), 400

    msg = enviar_mensagem_chat(candidatura_id, id_usuario, tipo, conteudo)
    return jsonify({
        "id": msg.id,
        "conteudo": msg.conteudo,
        "tipo_remetente": msg.tipo_remetente,
        "remetente_id": msg.remetente_id,
        "data": msg.data.strftime('%H:%M'),
    })


@chat_bp.route('/chat/<int:candidatura_id>/poll')
@login_required
def poll_mensagens(candidatura_id):
    candidatura = Candidatura.query.get_or_404(candidatura_id)
    id_usuario = session["id_usuario"]
    tipo = session["tipo_usuario"]

    if tipo == "dev" and candidatura.dev_id != id_usuario:
        abort(403)
    if tipo == "cliente" and candidatura.id_cliente != id_usuario:
        abort(403)

    ultimo_id = int(request.args.get("ultimo_id", 0))
    mensagens = ler_mensagens_chat(candidatura_id, ultimo_id)

    cand = Candidatura.query.get(candidatura_id)
    return jsonify({
        "status": cand.status,
        "mensagens": [{
            "id": m.id,
            "conteudo": m.conteudo,
            "tipo_remetente": m.tipo_remetente,
            "remetente_id": m.remetente_id,
            "data": m.data.strftime("%%H:%%M"),
        } for m in mensagens]
    })

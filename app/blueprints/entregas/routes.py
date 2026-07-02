from flask import Blueprint, session, abort, send_from_directory

from app import app
from app.models import Entrega
from app.decorators import login_required

# Blueprint próprio (em vez de ficar dentro de "cliente" ou "dev") porque a
# rota de download é usada pelos dois perfis: o cliente baixa a entrega para
# conferir, e o dev também pode reabrir o próprio arquivo já enviado.
entregas_bp = Blueprint('entregas', __name__)


@entregas_bp.route('/entrega/<int:entrega_id>/baixar')
@login_required
def baixar_entrega(entrega_id):
    entrega = Entrega.query.get_or_404(entrega_id)
    if session["id_usuario"] not in (entrega.id_cliente, entrega.dev_id):
        abort(403)

    diretorio_uploads_entregas = app.config['UPLOADS_PRIVADOS_DIR']
    return send_from_directory(
        diretorio_uploads_entregas,
        entrega.caminho_arquivo,
        as_attachment=True,
        download_name=entrega.nome_arquivo,
    )

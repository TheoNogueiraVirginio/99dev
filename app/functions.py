import csv
import hashlib
import uuid
from pathlib import Path
import os

from flask import session
from flask_mail import Message
import bcrypt
from app import mail, serializer
from app.models import Cliente, Desenvolvedor, Pagamento, db

import secrets

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DEMANDAS_CSV_PATH = DATA_DIR / 'demandas.csv'
SUPORTE_CSV_PATH = DATA_DIR / 'suporte.csv'
SUPORTE_DEV_CSV_PATH = DATA_DIR / 'suporte_dev.csv'
AVALIACOES_CSV_PATH = DATA_DIR / 'avaliacoes.csv'


def cadastrar_usuario(email, senha, cargo):
    usuario_existente = bool(
        Cliente.query.filter_by(email=email).first() or
        Desenvolvedor.query.filter_by(email=email).first()
    )
    if usuario_existente:
        raise ValueError("Este e-mail já está cadastrado no sistema.")

    senha_bytes = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_bytes, salt)

    if cargo == 'dev':
        novo_usuario = Desenvolvedor(email=email, senha=senha_hash.decode('utf-8'))
    else:
        novo_usuario = Cliente(email=email, senha=senha_hash.decode('utf-8'))

    db.session.add(novo_usuario)
    db.session.commit()
    return novo_usuario


def autenticar_usuario(email, senha):
    usuario = (
        Cliente.query.filter_by(email=email).first() or
        Desenvolvedor.query.filter_by(email=email).first()
    )
    if not usuario:
        raise ValueError("Usuário não encontrado")

    if not bcrypt.checkpw(senha.encode('utf-8'), usuario.senha.encode('utf-8')):
        raise ValueError("Senha incorreta")
    return usuario


def gerenciar_login_google(email, cargo):
    usuario = (
        Cliente.query.filter_by(email=email).first() or
        Desenvolvedor.query.filter_by(email=email).first()
    )
    if usuario:
        return usuario

    senha_aleatoria = secrets.token_urlsafe(32)
    try:
        novo_usuario = cadastrar_usuario(email, senha_aleatoria, cargo)
        return novo_usuario
    except Exception as e:
        raise ValueError(f"Erro ao criar conta automaticamente via Google: {str(e)}")


def atualizar_perfil_dev(id_dev, nome, titulo, valor_hora, skills, resumo,
                          github, linkedin, foto_perfil, foto_banner, novo_exibir_dados):
    perfil = Desenvolvedor.query.get(id_dev)
    if not perfil:
        raise ValueError("Perfil de desenvolvedor não encontrado.")

    perfil.nome = nome
    perfil.titulo = titulo
    perfil.valor_hora = valor_hora
    perfil.skills = skills
    perfil.resumo = resumo
    perfil.github = github
    perfil.linkedin = linkedin

    if foto_perfil:
        perfil.foto_perfil = salvar_foto_perfil(id_dev, foto_perfil)
    if foto_banner:
        perfil.foto_banner = salvar_banner_perfil(id_dev, foto_banner)

    perfil.exibir_dados = novo_exibir_dados

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def exibirSaldo(id_dev):
    perfil = Desenvolvedor.query.get(id_dev)
    if not perfil:
        raise ValueError("Perfil de desenvolvedor não encontrado.")
    return perfil.saldo


def atualizar_perfil_cliente(id_cliente, novo_email, nova_senha, nova_descricao, arquivo_foto):
    perfil = Cliente.query.get(id_cliente)
    if not perfil:
        raise ValueError("Usuário não encontrado.")

    if perfil.email != novo_email:
        if Cliente.query.filter_by(email=novo_email).first():
            raise ValueError("Este e-mail já está associado a outra conta.")
        perfil.email = novo_email

    if nova_senha:
        senha_bytes = nova_senha.encode('utf-8')
        salt = bcrypt.gensalt()
        perfil.senha = bcrypt.hashpw(senha_bytes, salt).decode('utf-8')

    if arquivo_foto:
        perfil.foto_perfil = salvar_foto_perfil(id_cliente, arquivo_foto)

    perfil.descricao = nova_descricao

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def salvar_foto_perfil(id_usuario, arquivo_foto):
    _, extensao = os.path.splitext(arquivo_foto.filename)
    nome_arquivo = f"{id_usuario}{extensao}"
    pasta_uploads = os.path.join(BASE_DIR, 'static', 'uploads', 'perfil')
    os.makedirs(pasta_uploads, exist_ok=True)
    arquivo_foto.save(os.path.join(pasta_uploads, nome_arquivo))
    return nome_arquivo


def salvar_banner_perfil(id_usuario, arquivo_banner):
    _, extensao = os.path.splitext(arquivo_banner.filename)
    nome_arquivo = f"{id_usuario}{extensao}"
    pasta_uploads = os.path.join(BASE_DIR, 'static', 'uploads', 'banner')
    os.makedirs(pasta_uploads, exist_ok=True)
    arquivo_banner.save(os.path.join(pasta_uploads, nome_arquivo))
    return nome_arquivo


def solicitar_recuperacao_senha(email):
    usuario = (
        Cliente.query.filter_by(email=email).first() or
        Desenvolvedor.query.filter_by(email=email).first()
    )
    if not usuario:
        raise ValueError("Usuário não encontrado")
    enviar_instrucoes(email)
    return True


def enviar_instrucoes(email):
    msg = Message(subject="Instruções para Recuperação de Senha - 99Dev", recipients=[email])
    token = gerar_token(email)
    msg.html = f"""
        <p>Olá, {email}.</p>
        <p>Recebemos uma solicitação para redefinir a senha da sua conta.</p>
        <p>Para criar uma nova senha, clique no botão abaixo:</p>
        <p>
        <a href="http://127.0.0.1:3001/nova-senha/{token}"
           style="padding:10px 16px;background:#2563eb;color:#fff;text-decoration:none;border-radius:6px;">
            Redefinir senha
        </a>
        </p>
        <p>Se você não solicitou essa alteração, pode ignorar este e-mail com segurança.</p>
        <p>Por motivos de segurança, este link expirará em 30 minutos.</p>
        <p>Atenciosamente,<br>Equipe 99Dev</p>
    """
    mail.send(msg)
    return "email enviado com sucesso"


def atualizar_senha(email, nova_senha):
    usuario = (
        Cliente.query.filter_by(email=email).first() or
        Desenvolvedor.query.filter_by(email=email).first()
    )
    if not usuario:
        raise ValueError("Usuário não encontrado")

    senha_bytes = nova_senha.encode('utf-8')
    salt = bcrypt.gensalt()
    usuario.senha = bcrypt.hashpw(senha_bytes, salt).decode('utf-8')

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def gerar_token(email):
    return serializer.dumps(email, salt='recuperar-senha')


def validar_token(token, expiracao=1800):
    try:
        return serializer.loads(token, salt='recuperar-senha', max_age=expiracao)
    except Exception:
        return None


# ─── UUID helper ──────────────────────────────────────────────────────────────

def _uuid_legado(titulo, id_cliente):
    """UUID determinístico para linhas antigas do CSV (sem coluna uuid)."""
    return hashlib.md5(f"{titulo}{id_cliente}".encode()).hexdigest()


# ─── Demandas (CSV) ───────────────────────────────────────────────────────────

def salvarDemanda(titulo, tecnologia, descricao, orcamento, status, id):
    demanda_uuid = str(uuid.uuid4())
    DEMANDAS_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DEMANDAS_CSV_PATH.open('a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow([titulo, tecnologia, descricao, orcamento, status, id, demanda_uuid])


def lerDemandas(tipo_usuario="cliente", id_usuario=None, busca=None, filtro_status=None):
    demandas = []
    if DEMANDAS_CSV_PATH.exists():
        with DEMANDAS_CSV_PATH.open('r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                # Garante que a linha tem o número mínimo de colunas
                if len(row) >= 6:
                    demanda = {
                        'titulo': row[0],
                        'tecnologia': row[1],
                        'descricao': row[2],
                        'orcamento': row[3],
                        'status': row[4].strip(),
                        'id': row[5].strip()
                    }
                    
                    # 1. Aplica o Filtro de Busca (barra de pesquisa)
                    if busca:
                        termo = busca.lower()
                        # Se o termo não estiver no título nem na tecnologia, pula esta linha
                        if termo not in demanda['titulo'].lower() and termo not in demanda['tecnologia'].lower():
                            continue
                            
                    # 2. Aplica o Filtro de Status (dropdown de categorias)
                    if filtro_status and filtro_status != 'Todos':
                        if demanda['status'] != filtro_status:
                            continue

                    # 3. Regras de Exibição por Tipo de Perfil
                    if tipo_usuario == "dev":
                        # O Dev vê as disponíveis e as que estão no fluxo de trabalho dele
                        if demanda['status'] in ["Aberta", "Em Andamento", "Aguardando Aprovação"]:
                            demandas.append(demanda)
                    else:
                        # O Cliente vê tudo (filtrado pela busca, se houver)
                        demandas.append(demanda)
                        
    return demandas

def atualizar_status_demanda(demanda_uuid, novo_status):
    """Atualiza o status de uma demanda no CSV pelo seu UUID."""
    if not DEMANDAS_CSV_PATH.exists():
        return False

    rows = []
    atualizado = False

    with DEMANDAS_CSV_PATH.open('r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            if len(row) >= 6:
                row_uuid = (
                    row[6].strip()
                    if len(row) > 6 and row[6].strip()
                    else _uuid_legado(row[0], row[5])
                )
                if row_uuid == demanda_uuid:
                    row[4] = novo_status
                    if len(row) < 7:
                        row.append(row_uuid)
                    atualizado = True
            rows.append(row)

    if atualizado:
        with DEMANDAS_CSV_PATH.open('w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerows(rows)

    return atualizado


# ─── Candidaturas ─────────────────────────────────────────────────────────────

def candidatar_dev(dev_id, demanda_uuid, demanda_titulo, id_cliente, proposta):
    from app.models import Candidatura

    existente = Candidatura.query.filter_by(
        dev_id=dev_id, demanda_uuid=demanda_uuid
    ).first()
    if existente:
        raise ValueError("Você já se candidatou a esta demanda.")

    nova = Candidatura(
        dev_id=dev_id,
        demanda_uuid=demanda_uuid,
        demanda_titulo=demanda_titulo,
        id_cliente=int(id_cliente),
        proposta=proposta,
        status='pendente',
    )
    db.session.add(nova)
    db.session.commit()

    atualizar_status_demanda(demanda_uuid, 'Pendente')

    return nova


def ler_projetos_dev(dev_id):
    """Retorna candidaturas aceitas do dev, enriquecidas com dados da demanda do CSV."""
    from app.models import Candidatura

    aceitas = Candidatura.query.filter_by(dev_id=dev_id, status='aceita').order_by(
        Candidatura.data.desc()
    ).all()

    # Enriquecer com dados do CSV (orcamento, tecnologia, descricao)
    demanda_map = {}
    if DEMANDAS_CSV_PATH.exists():
        with DEMANDAS_CSV_PATH.open('r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) < 6:
                    continue
                row_uuid = (
                    row[6].strip()
                    if len(row) > 6 and row[6].strip()
                    else _uuid_legado(row[0], row[5])
                )
                demanda_map[row_uuid] = {
                    'titulo':     row[0],
                    'tecnologia': row[1],
                    'descricao':  row[2],
                    'orcamento':  row[3],
                    'status':     row[4],
                }

    projetos = []
    for c in aceitas:
        info = demanda_map.get(c.demanda_uuid, {})
        projetos.append({
            'candidatura':  c,
            'titulo':       info.get('titulo',     c.demanda_titulo),
            'tecnologia':   info.get('tecnologia', '—'),
            'descricao':    info.get('descricao',  ''),
            'orcamento':    info.get('orcamento',  '—'),
            'status_demanda': info.get('status',   'Em Desenvolvimento'),
        })

    return projetos


def ler_candidaturas_dev(dev_id):
    from app.models import Candidatura
    return Candidatura.query.filter_by(dev_id=dev_id).order_by(
        Candidatura.data.desc()
    ).all()


def ler_candidaturas_cliente(id_cliente):
    from app.models import Candidatura
    return Candidatura.query.filter_by(id_cliente=id_cliente).order_by(
        Candidatura.data.desc()
    ).all()


# ─── Chat ─────────────────────────────────────────────────────────────────────

def enviar_mensagem_chat(candidatura_id, remetente_id, tipo_remetente, conteudo):
    from app.models import MensagemChat

    msg = MensagemChat(
        candidatura_id=candidatura_id,
        remetente_id=remetente_id,
        tipo_remetente=tipo_remetente,
        conteudo=conteudo,
    )
    db.session.add(msg)
    db.session.commit()
    return msg


def ler_mensagens_chat(candidatura_id, ultimo_id=0):
    from app.models import MensagemChat

    return (
        MensagemChat.query
        .filter(
            MensagemChat.candidatura_id == candidatura_id,
            MensagemChat.id > ultimo_id,
        )
        .order_by(MensagemChat.data.asc())
        .all()
    )


# ─── Saldo / Pagamentos ───────────────────────────────────────────────────────

def adicionar_saldo_cliente(id_cliente, saldo):
    perfil = Cliente.query.get(id_cliente)
    if not perfil:
        raise ValueError("Cliente não encontrado.")
    perfil.saldo += saldo
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def registrar_pagamento(id_cliente, titulo_demanda, valor):
    novo_pagamento = Pagamento(
        id_cliente=id_cliente,
        titulo_demanda=titulo_demanda,
        valor=valor,
    )
    db.session.add(novo_pagamento)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def ler_pagamentos_cliente(id_cliente):
    return Pagamento.query.filter_by(id_cliente=id_cliente).order_by(
        Pagamento.data_pagamento.desc()
    ).all()


def ler_demandas_realizadas_cliente(id_cliente):
    demandas_realizadas = []
    if DEMANDAS_CSV_PATH.exists():
        with DEMANDAS_CSV_PATH.open('r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                if len(row) < 6:
                    continue
                if row[5].strip().isdigit() and int(row[5]) == id_cliente:
                    if row[4].strip() in ["Fechada", "Concluída"]:
                        demandas_realizadas.append({
                            'titulo': row[0],
                            'tecnologia': row[1],
                            'descricao': row[2],
                            'orcamento': row[3],
                            'status': row[4],
                            'id': row[5],
                        })
    return demandas_realizadas

def atualizar_status_por_titulo(titulo_demanda, id_cliente, novo_status):
    linhas = []
    atualizado = False
    
    if DEMANDAS_CSV_PATH.exists():
        with DEMANDAS_CSV_PATH.open('r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            
            for row in reader:
                if len(row) >= 6:
                    if row[0] == titulo_demanda and str(row[5]) == str(id_cliente):
                        row[4] = novo_status  
                        atualizado = True
                linhas.append(row)
                
        if atualizado:
            with DEMANDAS_CSV_PATH.open('w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter='\t')
                writer.writerows(linhas)
                
    return atualizado

# ─── Suporte ──────────────────────────────────────────────────────────────────

def salvar_mensagem_suporte(id_usuario, tipo_usuario, assunto, mensagem):
    import datetime
    data_envio = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with SUPORTE_CSV_PATH.open('a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow([data_envio, id_usuario, tipo_usuario, assunto, mensagem])


def salvar_mensagem_suporte_dev(id_dev, assunto, mensagem):
    import datetime
    data_envio = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with SUPORTE_DEV_CSV_PATH.open('a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow([data_envio, id_dev, assunto, mensagem])
        
def salvar_avaliacao(titulo_demanda, id_avaliador, tipo_avaliador, id_avaliado, nota, comentario):
    import datetime
    data_registro = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with AVALIACOES_CSV_PATH.open('a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow([data_registro, titulo_demanda, id_avaliador, tipo_avaliador, id_avaliado, nota, comentario])
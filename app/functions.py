import csv
from pathlib import Path

import os

from flask import session
from flask_mail import Message
import bcrypt
from app import mail, serializer
from app.models import Cliente, Desenvolvedor, Pagamento, db

import secrets

BASE_DIR = Path(__file__).resolve().parent.parent
DEMANDAS_CSV_PATH = BASE_DIR / 'data' / 'demandas.csv'


def cadastrar_usuario(email,senha,cargo):
    usuario_existente = bool(Cliente.query.filter_by(email=email).first() or Desenvolvedor.query.filter_by(email=email).first())

    if usuario_existente:
        raise ValueError("Este e-mail já está cadastrado no sistema.")
    
    senha_bytes = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_bytes, salt)

    if cargo == 'dev':
        novo_usuario = Desenvolvedor(
            email=email,
            senha=senha_hash.decode('utf-8')
        )
    else:
        novo_usuario = Cliente(
            email=email,
            senha=senha_hash.decode('utf-8')
        )
    db.session.add(novo_usuario)
    db.session.commit()
    return novo_usuario

def autenticar_usuario(email,senha):
    usuario = Cliente.query.filter_by(email=email).first() or Desenvolvedor.query.filter_by(email=email).first()

    if not usuario:
        raise ValueError("Usuário não encontrado")
    
    senha_usuario = senha.encode('utf-8')
    senha_banco = usuario.senha.encode('utf-8')
    if not bcrypt.checkpw(senha_usuario, senha_banco):
        raise ValueError("Senha incorreta")    
    return usuario

def gerenciar_login_google(email, cargo):
    usuario = Cliente.query.filter_by(email=email).first() or Desenvolvedor.query.filter_by(email=email).first()
    
    if usuario:
        return usuario
    
    senha_aleatoria = secrets.token_urlsafe(32)
    try:
        novo_usuario = cadastrar_usuario(email, senha_aleatoria, cargo)
        return novo_usuario
    except Exception as e:
        raise ValueError(f"Erro ao criar conta automaticamente via Google: {str(e)}")
        
def atualizar_perfil_dev(id_dev, nome, titulo, valor_hora, skills, resumo, github, linkedin, foto_perfil, foto_banner, novo_exibir_dados):
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
        nome_da_foto = salvar_foto_perfil(id_cliente, arquivo_foto)
        perfil.foto_perfil = nome_da_foto

    perfil.descricao = nova_descricao
    
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

def salvar_foto_perfil(id_usuario, arquivo_foto):
    
    #Extrai a extensão
    _, extensao = os.path.splitext(arquivo_foto.filename)
    nome_arquivo = f"{id_usuario}{extensao}"
    pasta_uploads = os.path.join(BASE_DIR, 'static', 'uploads', 'perfil')
    os.makedirs(pasta_uploads, exist_ok=True)
    caminho_completo = os.path.join(pasta_uploads, nome_arquivo)
    arquivo_foto.save(caminho_completo)
    
    return nome_arquivo

def salvar_banner_perfil(id_usuario, arquivo_banner):
    _, extensao = os.path.splitext(arquivo_banner.filename)
    nome_arquivo = f"{id_usuario}{extensao}"
    pasta_uploads = os.path.join(BASE_DIR, 'static', 'uploads', 'banner')
    os.makedirs(pasta_uploads, exist_ok=True)
    caminho_completo = os.path.join(pasta_uploads, nome_arquivo)
    arquivo_banner.save(caminho_completo)

    return nome_arquivo

def solicitar_recuperacao_senha(email):
    usuario = Cliente.query.filter_by(email=email).first() or Desenvolvedor.query.filter_by(email=email).first()
    if not usuario:
        raise ValueError("Usuário não encontrado")
    
    enviar_instrucoes(email)
    print(f"Instruções de recuperação de senha enviadas para {email}")
    return True

#link direto
def enviar_instrucoes(email):
    msg = Message(
        subject="Instruções para Recuperação de Senha - 99Dev",
        recipients=[email],
    )
    token = gerar_token(email)
    msg.html = f"""
        <p>Olá, {email}.</p>

        <p>Recebemos uma solicitação para redefinir a senha da sua conta.</p>

        <p>Para criar uma nova senha, clique no botão abaixo:</p>

        <p>
        <a href="http://127.0.0.1:3001/nova-senha/{token}" style="padding:10px 16px;background:#2563eb;color:#fff;text-decoration:none;border-radius:6px;">
            Redefinir senha
        </a>
        </p>

        <p>Se você não solicitou essa alteração, pode ignorar este e-mail com segurança. Sua senha atual continuará funcionando normalmente.</p>

        <p>Por motivos de segurança, este link expirará em 30 minutos.</p>

        <p>Atenciosamente,<br>Equipe 99Dev</p>
    """
    mail.send(msg)
    print(f"Email de recuperação de senha enviado para {email}")

    return "email enviado com sucesso"

def atualizar_senha(email, nova_senha):
    usuario = Cliente.query.filter_by(email=email).first() or Desenvolvedor.query.filter_by(email=email).first()
    if not usuario:
        raise ValueError("Usuário não encontrado")
    
    #Criptografia redefinição de senha
    senha_bytes = nova_senha.encode('utf-8')
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_bytes, salt)
    
    usuario.senha = senha_hash.decode('utf-8')
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    
def gerar_token(email):
    return serializer.dumps(email, salt='recuperar-senha')

def validar_token(token, expiracao=1800):
    try:
        email = serializer.loads(
            token,
            salt='recuperar-senha',
            max_age=expiracao
        )
        return email
    except:
        return None

def salvarDemanda(titulo, tecnologia, descricao, orcamento, status, id):
    DEMANDAS_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DEMANDAS_CSV_PATH.open('a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow([titulo, tecnologia, descricao, orcamento, status, id])

def lerDemandas(busca=None, filtro_status=None, tipo_usuario=None):
    demandas = []
    demandasDev = []
    id_usuario = session.get("id_usuario")
    busca_normalizada = busca.lower().strip() if busca else None

    if DEMANDAS_CSV_PATH.exists():
        with DEMANDAS_CSV_PATH.open('r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                if len(row) < 6:
                    continue

                if not row[5].strip().isdigit():
                    continue

                if id_usuario is not None and int(row[5]) == id_usuario:
                    if filtro_status is not None and row[4] != filtro_status:
                        continue

                    if busca_normalizada:
                        texto_busca = " ".join([row[0], row[1], row[2], row[4]]).lower()
                        if busca_normalizada not in texto_busca:
                            continue

                    demandas.append({
                        'titulo': row[0],
                        'tecnologia': row[1],
                        'descricao': row[2],
                        'orcamento': row[3],
                        'status': row[4],
                        'id': row[5]
                    })
                demandasDev.append({
                    'titulo': row[0],
                    'tecnologia': row[1],
                    'descricao': row[2],
                    'orcamento': row[3],
                    'status': row[4],
                    'id': row[5]
                })
    if  tipo_usuario == "dev":
        return demandasDev
    return demandas

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
        valor=valor
    )
    
    db.session.add(novo_pagamento)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
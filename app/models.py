from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(256), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    foto_perfil = db.Column(db.String(150), nullable=True)
    saldo = db.Column(db.Float, default= 0, nullable=False)
    
class Desenvolvedor(db.Model):
    __tablename__ = 'perfis_dev'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(256), nullable=False)

    nome = db.Column(db.String(100), nullable=True)
    titulo = db.Column(db.String(100), nullable=True)
    valor_hora = db.Column(db.Integer, nullable=True)
    skills = db.Column(db.String(255), nullable=True)
    resumo = db.Column(db.Text, nullable=True)
    github = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    foto_perfil = db.Column(db.String(150), nullable=True)
    foto_banner = db.Column(db.String(150), nullable=True)
    saldo = db.Column(db.Float, default=1000.0, nullable=False)
    exibir_dados = db.Column(db.Boolean, default=True, nullable=False)
    
class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    titulo_demanda = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.DateTime, default=db.func.current_timestamp())


class Entrega(db.Model):
    __tablename__ = 'entregas'

    id = db.Column(db.Integer, primary_key=True)
    demanda_titulo = db.Column(db.String(255), nullable=False)
    id_cliente = db.Column(db.Integer, nullable=False)
    dev_id = db.Column(db.Integer, db.ForeignKey('perfis_dev.id'), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho_arquivo = db.Column(db.String(500), nullable=False)
    data_envio = db.Column(db.DateTime, default=db.func.current_timestamp())


class Candidatura(db.Model):
    __tablename__ = 'candidaturas'

    id = db.Column(db.Integer, primary_key=True)
    dev_id = db.Column(db.Integer, db.ForeignKey('perfis_dev.id'), nullable=False)
    demanda_uuid = db.Column(db.String(64), nullable=False)
    demanda_titulo = db.Column(db.String(255), nullable=False)
    id_cliente = db.Column(db.Integer, nullable=False)
    proposta = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pendente', nullable=False)
    data = db.Column(db.DateTime, default=db.func.current_timestamp())

    dev = db.relationship('Desenvolvedor', backref='candidaturas')
    mensagens = db.relationship('MensagemChat', backref='candidatura', lazy=True,
                                order_by='MensagemChat.data')


class MensagemChat(db.Model):
    __tablename__ = 'mensagens_chat'

    id = db.Column(db.Integer, primary_key=True)
    candidatura_id = db.Column(db.Integer, db.ForeignKey('candidaturas.id'), nullable=False)
    remetente_id = db.Column(db.Integer, nullable=False)
    tipo_remetente = db.Column(db.String(10), nullable=False)  # 'dev' ou 'cliente'
    conteudo = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=db.func.current_timestamp())
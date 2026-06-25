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

    # Dados extras (comentados como nullable=True para nascerem vazios no cadastro)
    nome = db.Column(db.String(100), nullable=True)
    titulo = db.Column(db.String(100), nullable=True)
    valor_hora = db.Column(db.Integer, nullable=True)
    skills = db.Column(db.String(255), nullable=True)
    resumo = db.Column(db.Text, nullable=True)
    github = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    foto_perfil = db.Column(db.String(150), nullable=True)
    foto_banner = db.Column(db.String(150), nullable=True)
    saldo = db.Column(db.Float,default=1000.0, nullable=False)
    exibir_dados = db.Column(db.Boolean, default=True, nullable=False)
    
class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    titulo_demanda = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_pagamento = db.Column(db.DateTime, default=db.func.current_timestamp())
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #nome_usuario = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(256), nullable=False)
    cargo = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    foto_perfil = db.Column(db.String(150), nullable=True)
    
class PerfilDev(db.Model):
    __tablename__ = 'perfis_dev'
    
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), unique=True, nullable=False)
    
    # Dados extras (comentados como nullable=True para nascerem vazios no cadastro)
    nome = db.Column(db.String(100), nullable=True)
    titulo = db.Column(db.String(100), nullable=True)
    valor_hora = db.Column(db.Integer, nullable=True)
    skills = db.Column(db.String(255), nullable=True)
    resumo = db.Column(db.Text, nullable=True)
    github = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    exibir_dados = db.Column(db.Boolean, default=True, nullable=False)
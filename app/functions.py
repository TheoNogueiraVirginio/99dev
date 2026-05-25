from flask_mail import Message

from app import mail
from app.models import Usuario, db

def cadastrar_usuario(email, senha, cargo_definido):
    novo_usuario = Usuario(
        email=email,
        senha=senha,
        cargo=cargo_definido
    )
    db.session.add(novo_usuario)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return novo_usuario

def solicitar_recuperacao_senha(email):
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        raise ValueError("Usuário não encontrado")
    
    enviar_instrucoes(email)
    print(f"Instruções de recuperação de senha enviadas para {email}")
    return True

def enviar_instrucoes(email):
    msg = Message(
        subject="Instruções para Recuperação de Senha - 99Dev",
        recipients=[email],
    )

    msg.body = "recuperar senha"
    mail.send(msg)
    print(f"Email de recuperação de senha enviado para {email}")

    return "email enviado com sucesso"

    



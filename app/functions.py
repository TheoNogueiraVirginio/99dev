from flask_mail import Message
import bcrypt
from app import mail, serializer
from app.models import Usuario, db


def cadastrar_usuario(email, senha, cargo_definido):
    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        raise ValueError("Este e-mail já está cadastrado no sistema.")

    #Criptografia
    senha_bytes = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_bytes, salt)
    
    novo_usuario = Usuario(
        email=email,
        senha=senha_hash.decode('utf-8'), 
        cargo=cargo_definido
    )
    db.session.add(novo_usuario)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return novo_usuario

def autenticar_usuario(email,senha):
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        raise ValueError("Usuário não encontrado")
    
    if usuario.senha != senha:
        raise ValueError("Senha incorreta")
    
    return usuario

def solicitar_recuperacao_senha(email):
    usuario = Usuario.query.filter_by(email=email).first()
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
    usuario = Usuario.query.filter_by(email=email).first()
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


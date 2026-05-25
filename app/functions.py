from app.models import db, Usuario

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

def recuperar_senha(email):
    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        raise ValueError("Usuário não encontrado")
    
    # Aqui você implementaria a lógica para enviar um email de recuperação de senha
    # Por exemplo, gerando um token e enviando um link para o email do usuário
    
    return True

    

    



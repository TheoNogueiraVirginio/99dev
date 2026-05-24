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

    

    



from functools import wraps
from flask import session, flash, redirect


def login_required(f):
    @wraps(f)

    def decorated_function(*args,**kwargs):
        if "id_usuario" not in session:
            flash("Você precisa estar logado para acessar esta página.", 'error')
            return redirect('/login')

        # Deixa a rota original rodar normalmente
        return f(*args, **kwargs)
    
    return decorated_function
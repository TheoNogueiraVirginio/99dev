from flask import flash, jsonify, render_template, redirect, request, session, abort, url_for

from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, FloatField
from wtforms.validators import input_required, Email, Optional, NumberRange

from app import app, db, google
from app.models import Cliente, Desenvolvedor, Candidatura, Pagamento
from app.functions import (
    atualizar_senha, cadastrar_usuario, autenticar_usuario, exibirSaldo,
    gerenciar_login_google, lerDemandas, salvarDemanda,
    solicitar_recuperacao_senha, validar_token, atualizar_perfil_dev,
    atualizar_perfil_cliente, adicionar_saldo_cliente, ler_pagamentos_cliente,
    ler_demandas_realizadas_cliente, salvar_mensagem_suporte,
    salvar_mensagem_suporte_dev, candidatar_dev, ler_candidaturas_dev, ler_candidaturas_cliente,
    enviar_mensagem_chat, ler_mensagens_chat, ler_projetos_dev, atualizar_status_demanda, salvar_avaliacao
)

from app.decorators import login_required

with app.app_context():
    db.create_all()

# ─── Forms ────────────────────────────────────────────────────────────────────

class CadastroForm(FlaskForm):
    email = StringField('Email', validators=[Email(message="Email inválido")])
    senha = PasswordField('senha', validators=[input_required()])
    dev = BooleanField('Eu sou um dev')
    pessoa = BooleanField('Eu preciso de um dev')

class RecuperarSenhaForm(FlaskForm):
    email = StringField('Email', validators=[Email(message="Email inválido")])

class NovaSenhaForm(FlaskForm):
    password = PasswordField('Nova Senha', validators=[input_required()])
    password_confirm = PasswordField('Confirme a Nova Senha', validators=[input_required()])

class EditarPerfilForm(FlaskForm):
    email = StringField('Email', validators=[Email(message="Email inválido")])
    nova_senha = PasswordField('Nova Senha (opcional)', validators=[Optional()])
    dev = BooleanField('Eu sou um dev')
    pessoa = BooleanField('Eu preciso de um dev')
    descricao = TextAreaField('Sobre Mim / Descrição', validators=[Optional()])
    foto = FileField('Foto de Perfil', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens .jpg, .jpeg ou .png!')])

class EditarDevForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[input_required(message="O nome é obrigatório.")])
    titulo = StringField('Função principal do Perfil', validators=[Optional()])
    valor_hora = IntegerField('Valor Hora (R$)', validators=[Optional()])
    skills = StringField('Habilidades (Tags)', validators=[Optional()])
    resumo = TextAreaField('Sobre Mim / Bio', validators=[Optional()])
    github = StringField('GitHub', validators=[Optional()])
    linkedin = StringField('LinkedIn', validators=[Optional()])
    exibir_dados = BooleanField('Exibir minhas estatísticas e avaliações publicamente')
    foto_perfil = FileField('Foto de Perfil', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens .jpg, .jpeg ou .png!')])
    foto_banner = FileField('Foto de Banner', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens .jpg, .jpeg ou .png!')])

class DemandaForm(FlaskForm):
    titulo = StringField('Título do Projeto', validators=[input_required(message="O título é obrigatório.")])
    tecnologia = StringField('Tecnologia Principal', validators=[input_required(message="A tecnologia é obrigatória.")])
    descricao = TextAreaField('Descrição Detalhada', validators=[input_required(message="A descrição é obrigatória.")])
    orcamento = IntegerField('Orçamento Estimado (R$)', validators=[input_required(message="O orçamento é obrigatório."),NumberRange(min=1, message="O valor tem que ser maior que 0 e ser inteiro")])

class FiltroForm(FlaskForm):
    filtro = StringField('Filtrar por status')

class SuporteForm(FlaskForm):
    assunto = StringField('Assunto do Contato', validators=[input_required(message="Por favor, insira o assunto da sua mensagem.")])
    mensagem = TextAreaField('Descrição detalhada do problema ou dúvida', validators=[input_required(message="O campo de mensagem não pode ficar vazio.")])

class SuporteDevForm(FlaskForm):
    assunto = StringField('Assunto da Solicitação', validators=[input_required(message="O assunto é obrigatório.")])
    mensagem = TextAreaField('Detalhes do Problema ou Dúvida', validators=[input_required(message="A mensagem não pode ficar vazia.")])

class AdicionarSaldoForm(FlaskForm):
    valor = FloatField('Valor do Depósito (R$)', validators=[input_required(message="Digite um valor para depositar."), NumberRange(min=0.01, message="O valor tem que ser maior que 0")])
    
class AvaliacaoForm(FlaskForm):
    nota = IntegerField('Nota', validators=[input_required(message="Escolha uma nota de 1 a 5.")])
    comentario = TextAreaField('Comentário', validators=[input_required(message="Deixe uma descrição.")])

# ─── Rotas existentes ─────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template('home.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroForm()
    if form.validate_on_submit():
        cargo_definido = 'dev' if form.dev.data else 'cliente'
        try:
            cadastrar_usuario(email=form.email.data, senha=form.senha.data, cargo=cargo_definido)
        except Exception as e:
            flash(f"Falha ao cadastrar usuário: {str(e)}", "error")
            return render_template('cadastro.html', form=form, error=str(e))
        return redirect('/login')
    return render_template('cadastro.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = CadastroForm()
    if form.validate_on_submit():
        try:
            usuario = autenticar_usuario(form.email.data, form.senha.data)
            session["id_usuario"] = usuario.id
            session["tipo_usuario"] = "dev" if isinstance(usuario, Desenvolvedor) else "cliente"
            flash("Login realizado com sucesso!", "success")
            if session["tipo_usuario"] == 'dev':
                return redirect('/DashboardDev')
            return redirect('/dashboard')
        except ValueError as e:
            flash(str(e), "error")
    return render_template('login.html', form=form)

@app.route('/login/google')
def login_google():
    session['cargo_pretendido'] = request.args.get('cargo', 'cliente')
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize/google')
def authorize_google():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        email = user_info['email']
        cargo_escolhido = session.pop('cargo_pretendido', 'cliente')
        usuario = gerenciar_login_google(email, cargo_escolhido)
        session["id_usuario"] = usuario.id
        session["tipo_usuario"] = "dev" if isinstance(usuario, Desenvolvedor) else "cliente"
        flash("Login com Google realizado com sucesso!", "success")
        if session["tipo_usuario"] == "dev":
            return redirect("/DashboardDev")
        return redirect("/dashboard")
    except Exception:
        flash("Ocorreu um erro ao tentar fazer login com o Google.", "error")
        return redirect('/login')

@app.route('/recuperar-senha', methods=['GET', 'POST'])
def recuperar_senha():
    form = RecuperarSenhaForm()
    if form.validate_on_submit():
        try:
            solicitar_recuperacao_senha(form.email.data)
            flash("Instruções para recuperação de senha enviadas para seu email", "success")
        except Exception as e:
            flash(f"Falha ao enviar email: {str(e)}", "error")
    return render_template('recuperar-senha.html', form=form)

@app.route('/nova-senha/<token>', methods=['GET', 'POST'])
def nova_senha(token):
    form = NovaSenhaForm()
    if form.validate_on_submit():
        if form.password.data != form.password_confirm.data:
            flash("As senhas não coincidem", "error")
            return render_template('nova-senha.html', form=form)
        email = validar_token(token)
        if not email:
            flash("Token inválido ou expirado", "error")
            return redirect('/recuperar-senha')
        atualizar_senha(email=email, nova_senha=form.password.data)
        flash("Senha atualizada com sucesso", "success")
        return redirect('/login')
    return render_template('nova-senha.html', form=form)

@app.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    id_usuario = session.get("id_usuario")
    usuario = Cliente.query.get(id_usuario)
    if not usuario:
        flash("Usuário não encontrado.", "error")
        return redirect('/login')
    if session.get("tipo_usuario") == 'dev':
        abort(403)
    form = EditarPerfilForm()
    if form.validate_on_submit():
        try:
            atualizar_perfil_cliente(id_cliente=id_usuario, novo_email=form.email.data,
                                     nova_senha=form.nova_senha.data,
                                     nova_descricao=form.descricao.data,
                                     arquivo_foto=form.foto.data)
            flash("Perfil atualizado com sucesso!", "success")
            return redirect('/editar-perfil')
        except Exception as e:
            flash(str(e), "error")
    elif request.method == 'GET':
        form.email.data = usuario.email
        form.dev.data = (session.get("tipo_usuario") == 'dev')
        form.pessoa.data = (session.get("tipo_usuario") == 'cliente')
        form.descricao.data = usuario.descricao
    return render_template('perfil-editar.html', foto_perfil=usuario.foto_perfil, form=form)

@app.route('/perfil-dev', methods=['GET', 'POST'])
@login_required
def perfildev():
    form = EditarDevForm()
    if session.get("tipo_usuario") != "dev":
        abort(403)
    usuario = Desenvolvedor.query.get(session["id_usuario"])
    if request.method == 'GET' and usuario:
        form.nome.data = usuario.nome
        form.titulo.data = usuario.titulo
        form.valor_hora.data = usuario.valor_hora
        form.skills.data = usuario.skills
        form.resumo.data = usuario.resumo
        form.github.data = usuario.github
        form.linkedin.data = usuario.linkedin
        form.exibir_dados.data = usuario.exibir_dados
    if form.validate_on_submit():
        try:
            atualizar_perfil_dev(id_dev=session["id_usuario"], nome=form.nome.data,
                                  titulo=form.titulo.data, valor_hora=form.valor_hora.data,
                                  skills=form.skills.data, resumo=form.resumo.data,
                                  github=form.github.data, linkedin=form.linkedin.data,
                                  foto_perfil=form.foto_perfil.data,
                                  foto_banner=form.foto_banner.data,
                                  novo_exibir_dados=form.exibir_dados.data)
            flash("Perfil atualizado com sucesso!", "success")
            return redirect('/perfil-dev')
        except Exception as e:
            flash(f"Erro ao atualizar perfil: {str(e)}", "error")
    return render_template('perfil.html', form=form, usuario=usuario)

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboardCliente():
    form = DemandaForm()
    form_avaliacao = AvaliacaoForm()
    
    if session.get("tipo_usuario") != "cliente":
        abort(403)
    id = session["id_usuario"]
    usuario = Cliente.query.get(id)
    demandas = lerDemandas()
    pagamentos = ler_pagamentos_cliente(id)
    demandas_realizadas = ler_demandas_realizadas_cliente(id)
    candidaturas = ler_candidaturas_cliente(id)

    if form.validate_on_submit():
        try:
            salvarDemanda(titulo=form.titulo.data, tecnologia=form.tecnologia.data,
                          descricao=form.descricao.data, orcamento=form.orcamento.data,
                          status="Aberta", id=id)
            flash("Demanda cadastrada com sucesso!", "success")
            return redirect('/dashboard')
        except Exception as e:
            flash(f"Falha ao cadastrar demanda: {str(e)}", "error")
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, "error")
    return render_template('dashboardCliente.html', form=form, demandas=demandas, form_avaliacao=form_avaliacao,
                           foto_perfil=usuario.foto_perfil if usuario else None,
                           usuario=usuario, pagamentos=pagamentos,
                           demandas_realizadas=demandas_realizadas,
                           candidaturas=candidaturas)

@app.route("/MeusProjetos", methods=['GET', 'POST'])
@login_required
def meusProjetos():
    busca = request.args.get("busca", "").strip() or None
    filtro_status = request.args.get("filtro", "").strip() or None
    demandas = lerDemandas(busca=busca, filtro_status=filtro_status)
    return render_template('MeusProjetos.html', demandas=demandas)

@app.route("/logout", methods=['GET'])
def sairLogin():
    session.clear()
    flash('Você saiu da sua conta, logue novamente!')
    return redirect('/login')

@app.route("/DashboardDev", methods=['GET'])
@login_required
def dashboardDev():
    if session.get("tipo_usuario") != "dev":
        abort(403)
    id_dev = session["id_usuario"]
    usuario = Desenvolvedor.query.get(id_dev)
    demandas = lerDemandas(tipo_usuario="dev")
    saldo = exibirSaldo(id_dev)
    candidaturas = ler_candidaturas_dev(id_dev)
    foto_perfil = usuario.foto_perfil if usuario else None
    return render_template('dashboardDev.html', demandas=demandas, saldo=saldo,
                           usuario=usuario, foto_perfil=foto_perfil,
                           candidaturas=candidaturas)

@app.route('/adicionar-saldo', methods=['POST'])
@login_required
def adicionar_saldo():
    if session.get("tipo_usuario") != "cliente":
        abort(403)
    form = AdicionarSaldoForm()
    if form.validate_on_submit():
        try:
            adicionar_saldo_cliente(id_cliente=session["id_usuario"], saldo=form.valor.data)
            flash(f"Saldo de R$ {form.valor.data:.2f} adicionado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao processar o depósito: {str(e)}", "error")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error, "error")
    return redirect('/carteira')

@app.route('/carteira', methods=['GET', 'POST'])
@login_required
def carteiraCliente():
    if session.get("tipo_usuario") != "cliente":
        abort(403)
    id = session["id_usuario"]
    usuario = Cliente.query.get(id)
    form = AdicionarSaldoForm()
    return render_template('carteiraCliente.html', usuario=usuario, form=form,
                           foto_perfil=usuario.foto_perfil if usuario else None)

@app.errorhandler(403)
def acesso_proibido(error):
    return render_template('403.html'), 403

@app.route('/suporte', methods=['GET', 'POST'])
@login_required
def suporte():
    form = SuporteForm()
    id_usuario = session.get("id_usuario")
    tipo_usuario = session.get("tipo_usuario")
    usuario = Desenvolvedor.query.get(id_usuario) if tipo_usuario == 'dev' else Cliente.query.get(id_usuario)
    foto_perfil = usuario.foto_perfil if usuario else None
    if form.validate_on_submit():
        try:
            salvar_mensagem_suporte(id_usuario=id_usuario, tipo_usuario=tipo_usuario,
                                    assunto=form.assunto.data, mensagem=form.mensagem.data)
            flash("Sua mensagem foi enviada com sucesso à equipe de suporte!", "success")
            return redirect('/suporte')
        except Exception as e:
            flash(f"Ocorreu um erro ao tentar registrar sua mensagem: {str(e)}", "error")
    return render_template('suporte.html', form=form, foto_perfil=foto_perfil, usuario=usuario)

@app.route('/suporte-dev', methods=['GET', 'POST'])
@login_required
def suporteDev():
    if session.get("tipo_usuario") != "dev":
        abort(403)
    form = SuporteDevForm()
    id_dev = session["id_usuario"]
    usuario = Desenvolvedor.query.get(id_dev)
    foto_perfil = usuario.foto_perfil if usuario else None
    if form.validate_on_submit():
        try:
            salvar_mensagem_suporte_dev(id_dev=id_dev, assunto=form.assunto.data,
                                        mensagem=form.mensagem.data)
            flash("Ticket de suporte enviado com sucesso!", "success")
            return redirect('/suporte-dev')
        except Exception as e:
            flash(f"Ocorreu um erro ao enviar sua solicitação: {str(e)}", "error")
    return render_template('suporteDev.html', form=form, usuario=usuario, foto_perfil=foto_perfil)


@app.route("/MeusProjetosDev")
@login_required
def meusProjetosDev():
    if session.get("tipo_usuario") != "dev":
        abort(403)
    id_dev = session["id_usuario"]
    usuario = Desenvolvedor.query.get(id_dev)
    projetos = ler_projetos_dev(id_dev)
    return render_template('meusProjetosDev.html',
                           projetos=projetos,
                           usuario=usuario,
                           foto_perfil=usuario.foto_perfil if usuario else None)


# ─── Candidatura ──────────────────────────────────────────────────────────────

@app.route('/candidatar', methods=['POST'])
@login_required
def candidatar():
    if session.get("tipo_usuario") != "dev":
        abort(403)

    dev_id = session["id_usuario"]
    demanda_uuid = request.form.get("demanda_uuid", "").strip()
    demanda_titulo = request.form.get("demanda_titulo", "").strip()
    id_cliente = request.form.get("id_cliente", "").strip()
    proposta = request.form.get("proposta", "").strip()

    if not demanda_uuid or not demanda_titulo or not id_cliente:
        flash("Dados da demanda inválidos.", "error")
        return redirect('/DashboardDev')

    try:
        candidatura = candidatar_dev(
            dev_id=dev_id,
            demanda_uuid=demanda_uuid,
            demanda_titulo=demanda_titulo,
            id_cliente=int(id_cliente),
            proposta=proposta,
        )
        flash("Candidatura enviada! Agora você pode conversar com o cliente.", "success")
        return redirect(f'/chat/{candidatura.id}')
    except ValueError as e:
        flash(str(e), "error")
        return redirect('/DashboardDev')


# ─── Chat ─────────────────────────────────────────────────────────────────────

@app.route('/chat/<int:candidatura_id>')
@login_required
def chat(candidatura_id):
    candidatura = Candidatura.query.get_or_404(candidatura_id)
    id_usuario = session["id_usuario"]
    tipo = session["tipo_usuario"]

    if tipo == "dev" and candidatura.dev_id != id_usuario:
        abort(403)
    if tipo == "cliente" and candidatura.id_cliente != id_usuario:
        abort(403)

    dev = Desenvolvedor.query.get(candidatura.dev_id)
    cliente = Cliente.query.get(candidatura.id_cliente)
    mensagens = ler_mensagens_chat(candidatura_id)

    return render_template('chat.html',
                           candidatura=candidatura,
                           dev=dev,
                           cliente=cliente,
                           mensagens=mensagens,
                           tipo_usuario=tipo,
                           id_usuario=id_usuario)


@app.route('/chat/<int:candidatura_id>/enviar', methods=['POST'])
@login_required
def enviar_mensagem(candidatura_id):
    candidatura = Candidatura.query.get_or_404(candidatura_id)
    id_usuario = session["id_usuario"]
    tipo = session["tipo_usuario"]

    if tipo == "dev" and candidatura.dev_id != id_usuario:
        abort(403)
    if tipo == "cliente" and candidatura.id_cliente != id_usuario:
        abort(403)

    conteudo = request.json.get("conteudo", "").strip() if request.is_json else request.form.get("conteudo", "").strip()
    if not conteudo:
        return jsonify({"error": "Mensagem vazia"}), 400

    msg = enviar_mensagem_chat(candidatura_id, id_usuario, tipo, conteudo)
    return jsonify({
        "id": msg.id,
        "conteudo": msg.conteudo,
        "tipo_remetente": msg.tipo_remetente,
        "remetente_id": msg.remetente_id,
        "data": msg.data.strftime('%H:%M'),
    })


@app.route('/candidatura/<int:candidatura_id>/aceitar', methods=['POST'])
@login_required
def aceitar_candidatura(candidatura_id):
    if session.get("tipo_usuario") != "cliente":
        return jsonify({"error": "Apenas clientes podem aceitar propostas."}), 403

    candidatura = Candidatura.query.get_or_404(candidatura_id)
    if candidatura.id_cliente != session["id_usuario"]:
        return jsonify({"error": "Sem permissão."}), 403

    if candidatura.status != 'pendente':
        return jsonify({"error": "Esta candidatura não está mais pendente."}), 400

    from app.functions import enviar_mensagem_chat, atualizar_status_demanda
    candidatura.status = 'aceita'
    db.session.commit()
    atualizar_status_demanda(candidatura.demanda_uuid, 'Em Desenvolvimento')
    enviar_mensagem_chat(candidatura_id, session["id_usuario"], 'cliente',
                         '✅ Proposta aceita! O projeto agora está em desenvolvimento.')
    return jsonify({"ok": True, "status": "aceita"})


@app.route('/chat/<int:candidatura_id>/poll')
@login_required
def poll_mensagens(candidatura_id):
    candidatura = Candidatura.query.get_or_404(candidatura_id)
    id_usuario = session["id_usuario"]
    tipo = session["tipo_usuario"]

    if tipo == "dev" and candidatura.dev_id != id_usuario:
        abort(403)
    if tipo == "cliente" and candidatura.id_cliente != id_usuario:
        abort(403)

    ultimo_id = int(request.args.get("ultimo_id", 0))
    mensagens = ler_mensagens_chat(candidatura_id, ultimo_id)

    cand = Candidatura.query.get(candidatura_id)
    return jsonify({
        "status": cand.status,
        "mensagens": [{
            "id": m.id,
            "conteudo": m.conteudo,
            "tipo_remetente": m.tipo_remetente,
            "remetente_id": m.remetente_id,
            "data": m.data.strftime("%%H:%%M"),
        } for m in mensagens]
    })
    
@app.route("/entregar-demanda/<string:titulo>/<int:id_cliente>", methods=['POST'])
@login_required
def entregar_demanda(titulo, id_cliente):
    if session.get("tipo_usuario") != "dev":
        abort(403)
        
    try:
        sucesso = atualizar_status_demanda(titulo, id_cliente, "Aguardando Aprovação")
        
        if sucesso:
            flash("Entrega da demanda enviada com sucesso! Aguarde a aprovação do cliente.", "success")
        else:
            flash("Erro: Não foi possível localizar a demanda para entrega.", "error")
            
    except Exception as e:
        flash(f"Falha ao processar entrega da demanda: {str(e)}", "error")
        
    return redirect('/DashboardDev')

@app.route("/aprovar-demanda/<string:titulo>/<int:id_cliente>", methods=['POST'])
@login_required
def aprovar_demanda(titulo, id_cliente):
    if session.get("tipo_usuario") != "cliente":
        abort(403)
        
    try:
        sucesso = atualizar_status_demanda(titulo, id_cliente, "Concluída")
        
        if sucesso:
            candidatura = Candidatura.query.filter_by(
                demanda_titulo=titulo, 
                id_cliente=id_cliente, 
                status="Aceita"
            ).first()
            
            if candidatura:
                dev = Desenvolvedor.query.get(candidatura.dev_id)
                cliente = Cliente.query.get(id_cliente)
                
                todas_demandas = lerDemandas()
                orcamento = 0.0
                for d in todas_demandas:
                    if d['titulo'] == titulo and str(d['id']) == str(id_cliente):
                        orcamento = float(d['orcamento'])
                        break
                
                if cliente.saldo >= orcamento:
                    cliente.saldo -= orcamento
                    dev.saldo += orcamento
                    
                    novo_pagamento = Pagamento(
                        demanda_titulo=titulo,
                        valor=orcamento,
                        cliente_id=id_cliente,
                        dev_id=dev.id
                    )
                    db.session.add(novo_pagamento)
                    db.session.commit()
                    
                    flash("Projeto aprovado e pagamento transferido com sucesso ao desenvolvedor!", "success")
                else:
                    flash("Demanda aprovada, mas você não tem saldo suficiente. Recarregue a sua carteira.", "warning")
            else:
                flash("Demanda aprovada, mas não encontramos o Desenvolvedor para pagar.", "warning")
        else:
            flash("Erro: Não foi possível localizar a demanda indicada no sistema.", "error")
            
    except Exception as e:
        db.session.rollback() # Em caso de erro, desfaz a transação financeira por segurança
        flash(f"Falha ao processar aprovação da demanda: {str(e)}", "error")
        
    return redirect('/dashboard')

@app.route("/negar-demanda/<string:titulo>/<int:id_cliente>", methods=['POST'])
@login_required
def negar_demanda(titulo, id_cliente):
    if session.get("tipo_usuario") != "cliente":
        abort(403)
        
    try:
        sucesso = atualizar_status_demanda(titulo, id_cliente, "Em Andamento")
        if sucesso:
            flash("Entrega recusada. O projeto retornou para o status Em Andamento para correções.", "success")
        else:
            flash("Erro: Não foi possível localizar a demanda indicada.", "error")
    except Exception as e:
        flash(f"Falha ao processar recusa da entrega: {str(e)}", "error")
        
    return redirect('/dashboard')

@app.route("/avaliar-dev/<string:titulo>/<int:id_cliente>", methods=['POST'])
@login_required
def avaliar_dev(titulo, id_cliente):
    form = AvaliacaoForm()
    if session.get("tipo_usuario") != "cliente":
        abort(403)
        
    candidatura = Candidatura.query.filter_by(
        demanda_titulo=titulo, 
        id_cliente=id_cliente, 
        status="Aceita"
    ).first()
    
    if form.validate_on_submit() and candidatura:
        try:
            salvar_avaliacao(titulo, session["id_usuario"], "cliente", candidatura.dev_id, form.nota.data, form.comentario.data)
            flash("Avaliação do desenvolvedor registrada com sucesso!", "success")
        except Exception as e:
            flash("Erro ao salvar avaliação.", "error")
            
    return redirect('/dashboard')


# ─── main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, port=3001)
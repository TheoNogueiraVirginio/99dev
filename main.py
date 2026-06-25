from flask import flash, render_template, redirect, request, session, abort, url_for

from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, FloatField
from wtforms.validators import input_required, Email, Optional

#importando a função de cadastro do usuário
from app import app, db, google
from app.models import Cliente, Desenvolvedor

from app.functions import atualizar_senha, cadastrar_usuario, autenticar_usuario, exibirSaldo, gerenciar_login_google, lerDemandas, salvarDemanda, solicitar_recuperacao_senha, validar_token, atualizar_perfil_dev, atualizar_perfil_cliente, adicionar_saldo_cliente, ler_pagamentos_cliente, ler_demandas_realizadas_cliente

from app.decorators import login_required

with app.app_context():
    db.create_all()

## formulário de cadastro
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
    orcamento = IntegerField('Orçamento Estimado (R$)', validators=[input_required(message="O orçamento é obrigatório.")])

class FiltroForm(FlaskForm):
    filtro = StringField('Filtrar por status')
@app.route("/")
def home():
    return render_template('home.html')

class AdicionarSaldoForm(FlaskForm):
    valor = FloatField('Valor do Depósito (R$)', validators=[input_required(message="Digite um valor para depositar.")])

# rota provisoria
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    form = CadastroForm()
    
    #cadastro valido
    if form.validate_on_submit():
        
        if form.dev.data:
            cargo_definido = 'dev'
        else:
            cargo_definido = 'cliente'
            
        #envia payload para a função de cadastro do usuário
        try:
            cadastrar_usuario(
                email=form.email.data,
                senha=form.senha.data,
                cargo=cargo_definido
            )
        except Exception as e:
            flash(f"Falha ao cadastrar usuário: {str(e)}", "error")
            return render_template('cadastro.html', form=form, error=str(e))
        
        return redirect('/login')
        
    return render_template('cadastro.html', form=form)

@app.route('/login', methods=["GET","POST"])
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

#rota para iniciar a autenticação via Google
@app.route('/login/google')
def login_google():
    #Se não vier nada, assume 'cliente'
    session['cargo_pretendido'] = request.args.get('cargo', 'cliente')

    # Monta a URL de callback e redireciona o usuário para a tela do Google
    redirect_uri = url_for('authorize_google', _external=True)
    return google.authorize_redirect(redirect_uri)

#rota para callback de autorização do Google
@app.route('/authorize/google')
def authorize_google():
    try:
        # O usuário voltou do Google. Pegamos o token e os dados dele:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        email = user_info['email']
        
        cargo_escolhido = session.pop('cargo_pretendido', 'cliente')
        
        usuario = gerenciar_login_google(email, cargo_escolhido)
        
        session["id_usuario"] = usuario.id
        session["tipo_usuario"] = "dev" if isinstance(usuario, Desenvolvedor) else "cliente"
        flash("Login com Google realizado com sucesso!", "success")
        
        # 5. Redireciona para o painel correto
        if session["tipo_usuario"] == "dev":
            return redirect("/DashboardDev")
        return redirect("/dashboard")
            
    except Exception as e:
        flash("Ocorreu um erro ao tentar fazer login com o Google.", "error")
        return redirect('/login')

#rota para a página de recuperação de senha
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
 
#rota nova senha botar token de recuperação de senha depois
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
            atualizar_perfil_cliente(
                id_cliente=id_usuario,
                novo_email=form.email.data,
                nova_senha=form.nova_senha.data,
                nova_descricao=form.descricao.data,
                arquivo_foto=form.foto.data
            )
            flash("Perfil updated com sucesso!", "success")
            return redirect('/editar-perfil')
            
        except Exception as e:
            flash(str(e), "error")
            
    elif request.method == 'GET':
        form.email.data = usuario.email
        form.dev.data = (session.get("tipo_usuario") == 'dev')
        form.pessoa.data = (session.get("tipo_usuario") == 'cliente')
        form.descricao.data = usuario.descricao    
    foto_perfil= usuario.foto_perfil    
    return render_template('perfil-editar.html',foto_perfil=foto_perfil, form=form)

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
            id_do_usuario_logado = session["id_usuario"]
            
            
            atualizar_perfil_dev(
                id_dev=id_do_usuario_logado,
                nome=form.nome.data,
                titulo=form.titulo.data,
                valor_hora=form.valor_hora.data,
                skills=form.skills.data,
                resumo=form.resumo.data,
                github=form.github.data,
                linkedin=form.linkedin.data,
                foto_perfil=form.foto_perfil.data,
                foto_banner=form.foto_banner.data,
                novo_exibir_dados=form.exibir_dados.data
            )
            
            flash("Perfil atualizado com sucesso!", "success")
            return redirect('/perfil-dev')
            
        except Exception as e:
            flash(f"Erro ao atualizar perfil: {str(e)}", "error")
            
    return render_template('perfil.html', form=form, usuario=usuario)


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboardCliente():
    form = DemandaForm()

    if session.get("tipo_usuario") != "cliente":
        abort(403)

    id = session["id_usuario"]
    usuario = Cliente.query.get(id)
    demandas = lerDemandas()
    pagamentos = ler_pagamentos_cliente(id)
    demandas_realizadas = ler_demandas_realizadas_cliente(id)

    if form.validate_on_submit():
        try:
            salvarDemanda(
                titulo=form.titulo.data,
                tecnologia=form.tecnologia.data,
                descricao=form.descricao.data,
                orcamento=form.orcamento.data,
                status="Aberta",
                id=id
            )
            flash("Demanda cadastrada com sucesso!", "success")
            return redirect('/dashboard')
        except Exception as e:
            flash(f"Falha ao cadastrar demanda: {str(e)}", "error")
            
    foto_perfil = usuario.foto_perfil if usuario else None
    
    return render_template(
        'dashboardCliente.html', 
        form=form, 
        demandas=demandas, 
        foto_perfil=foto_perfil, 
        usuario=usuario, 
        pagamentos=pagamentos,
        demandas_realizadas=demandas_realizadas
    )
    
@app.route("/MeusProjetos", methods=['GET', 'POST'])
@login_required
def meusProjetos():
    busca = request.args.get("busca", "").strip() or None
    filtro_status = request.args.get("filtro", "").strip() or None
    demandas = lerDemandas(busca=busca, filtro_status=filtro_status)
    return render_template('MeusProjetos.html', demandas=demandas)

@app.route("/logout",methods=['GET'])
def sairLogin():
    session.clear()
    flash('Você saiu da sua conta, logue novamente!')
    return redirect ('/login')


##Rota para o dashboard do dev, só pode acessar se for dev, se for cliente da erro 403
@app.route("/DashboardDev",methods=['GET'])
@login_required
def dashboardDev():
    if session.get("tipo_usuario") != "dev":
        abort(403)

    demandas = lerDemandas(tipo_usuario="dev")
    saldo = exibirSaldo(session["id_usuario"])
    return render_template('dashboardDev.html', demandas=demandas, saldo=saldo)

@app.route("/mensagens")
@login_required
def chat():
    return render_template('chat.html')

@app.route('/adicionar-saldo', methods=['POST'])
@login_required
def adicionar_saldo():
    if session.get("tipo_usuario") != "cliente":
        abort(403)
        
    form = AdicionarSaldoForm()
    
    if form.validate_on_submit():
        try:
            id_cliente = session["id_usuario"]
            valor_deposito = form.valor.data
            
            adicionar_saldo_cliente(id_cliente=id_cliente, saldo=valor_deposito)
            
            flash(f"Saldo de R$ {valor_deposito:.2f} adicionado com sucesso!", "success")
        except Exception as e:
            flash(f"Erro ao processar o depósito: {str(e)}", "error")
            
    return redirect('/carteira')

@app.route('/carteira', methods=['GET', 'POST'])
@login_required
def carteiraCliente():
    if session.get("tipo_usuario") != "cliente":
        abort(403)
    
    id = session["id_usuario"]
    usuario = Cliente.query.get(id)
    form = AdicionarSaldoForm()
    foto_perfil = usuario.foto_perfil if usuario else None
    return render_template('carteiraCliente.html', usuario=usuario, form=form, foto_perfil=foto_perfil)

@app.errorhandler(403)
def acesso_proibido(error):
    return render_template('403.html'),403

# executa a aplicação
if __name__ == '__main__':
    app.run(debug=True, port=3001)
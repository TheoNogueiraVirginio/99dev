from flask import flash, render_template, redirect, request, session

from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, URLField
from wtforms.validators import input_required, Email, Optional, URL

#importando a função de cadastro do usuário
from app import app, db
from app.models import Usuario

from app.functions import atualizar_senha, cadastrar_usuario, autenticar_usuario, lerDemandas, salvarDemanda, solicitar_recuperacao_senha, validar_token, atualizar_perfil_dev, atualizar_perfil_cliente
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
    github = URLField('GitHub', validators=[Optional(), URL(message="Insira uma URL válida.")])
    linkedin = URLField('LinkedIn', validators=[Optional(), URL(message="Insira uma URL válida.")])

class DemandaForm(FlaskForm):
    titulo = StringField('Título do Projeto', validators=[input_required(message="O título é obrigatório.")])
    tecnologia = StringField('Tecnologia Principal', validators=[input_required(message="A tecnologia é obrigatória.")])
    descricao = TextAreaField('Descrição Detalhada', validators=[input_required(message="A descrição é obrigatória.")])
    orcamento = IntegerField('Orçamento Estimado (R$)', validators=[input_required(message="O orçamento é obrigatório.")])

class FiltroForm(FlaskForm):
    filtro = StringField('Filtrar por status')

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
                cargo_definido=cargo_definido
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
            flash("Login realizado com sucesso!", "success")
            if usuario.cargo=='dev':
                return redirect('/perfil-dev')
            else:
                return redirect('/dashboard')

        except ValueError as e:
            flash(str(e), "error")

    return render_template('login.html', form=form)

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
    usuario = Usuario.query.get(id_usuario)
    
    if not usuario:
        flash("Usuário não encontrado.", "error")
        return redirect('/login')
        
    form = EditarPerfilForm()
    
    if form.validate_on_submit():
        
        novo_cargo = 'dev' if form.dev.data else 'cliente'
            
        try:
            atualizar_perfil_cliente(
                id_usuario=id_usuario,
                novo_email=form.email.data,
                nova_senha=form.nova_senha.data,
                novo_cargo=novo_cargo,
                nova_descricao=form.descricao.data,
                arquivo_foto=form.foto.data
            )
            flash("Perfil updated com sucesso!", "success")
            return redirect('/editar-perfil')
            
        except Exception as e:
            flash(str(e), "error")
            
    elif request.method == 'GET':
        form.email.data = usuario.email
        form.dev.data = (usuario.cargo == 'dev')
        form.pessoa.data = (usuario.cargo == 'cliente')
        form.descricao.data = usuario.descricao    
        
    return render_template('perfil-editar.html', form=form)

@app.route('/perfil-dev', methods=['GET', 'POST'])
@login_required
def perfildev():
    form = EditarDevForm()
    
    if form.validate_on_submit():
        try:
            id_do_usuario_logado = session["id_usuario"]
            
            
            atualizar_perfil_dev(
                id_usuario=id_do_usuario_logado,
                nome=form.nome.data,
                titulo=form.titulo.data,
                valor_hora=form.valor_hora.data,
                skills=form.skills.data,
                resumo=form.resumo.data,
                github=form.github.data,
                linkedin=form.linkedin.data
            )
            
            flash("Perfil atualizado com sucesso!", "success")
            return redirect('/perfil-dev')
            
        except Exception as e:
            flash(f"Erro ao atualizar perfil: {str(e)}", "error")
            
    return render_template('perfil.html', form=form)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboardCliente():
    form = DemandaForm()
    id = session["id_usuario"]

    demandas = lerDemandas()

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

    return render_template('dashboardCliente.html', form=form, demandas=demandas)

@app.route("/MeusProjetos", methods=['GET', 'POST'])
@login_required
def meusProjetos():
    busca = request.args.get("busca", "").strip() or None
    filtro_status = request.args.get("filtro", "").strip() or None
    demandas = lerDemandas(busca=busca, filtro_status=filtro_status)
    return render_template('MeusProjetos.html', demandas=demandas)

# executa a aplicação
if __name__ == '__main__':
    app.run(debug=True, port=3001)
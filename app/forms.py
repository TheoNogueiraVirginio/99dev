"""Formulários (WTForms) usados pelas rotas da aplicação.

Ficavam todos soltos dentro de main.py. Foram centralizados aqui porque mais
de um blueprint usa o mesmo formulário (ex: AvaliacaoForm é usado tanto pelo
blueprint de cliente quanto poderia ser reaproveitado em outro lugar), e não
faz sentido cada blueprint redefinir a própria cópia da classe.
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, PasswordField, BooleanField, TextAreaField,
    IntegerField, FloatField,
)
from wtforms.validators import input_required, Email, Optional, NumberRange


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
    foto = FileField('Foto de Perfil', validators=[
        Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens .jpg, .jpeg ou .png!')
    ])


class EditarDevForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[input_required(message="O nome é obrigatório.")])
    titulo = StringField('Função principal do Perfil', validators=[Optional()])
    valor_hora = IntegerField('Valor Hora (R$)', validators=[Optional()])
    skills = StringField('Habilidades (Tags)', validators=[Optional()])
    resumo = TextAreaField('Sobre Mim / Bio', validators=[Optional()])
    github = StringField('GitHub', validators=[Optional()])
    linkedin = StringField('LinkedIn', validators=[Optional()])
    exibir_dados = BooleanField('Exibir minhas estatísticas e avaliações publicamente')
    foto_perfil = FileField('Foto de Perfil', validators=[
        Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens .jpg, .jpeg ou .png!')
    ])
    foto_banner = FileField('Foto de Banner', validators=[
        Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Apenas imagens .jpg, .jpeg ou .png!')
    ])


class DemandaForm(FlaskForm):
    titulo = StringField('Título do Projeto', validators=[input_required(message="O título é obrigatório.")])
    tecnologia = StringField('Tecnologia Principal', validators=[input_required(message="A tecnologia é obrigatória.")])
    descricao = TextAreaField('Descrição Detalhada', validators=[input_required(message="A descrição é obrigatória.")])
    orcamento = IntegerField('Orçamento Estimado (R$)', validators=[
        input_required(message="O orçamento é obrigatório."),
        NumberRange(min=1, message="O valor tem que ser maior que 0 e ser inteiro"),
    ])


class FiltroForm(FlaskForm):
    filtro = StringField('Filtrar por status')


class SuporteForm(FlaskForm):
    assunto = StringField('Assunto do Contato', validators=[input_required(message="Por favor, insira o assunto da sua mensagem.")])
    mensagem = TextAreaField('Descrição detalhada do problema ou dúvida', validators=[input_required(message="O campo de mensagem não pode ficar vazio.")])


class SuporteDevForm(FlaskForm):
    assunto = StringField('Assunto da Solicitação', validators=[input_required(message="O assunto é obrigatório.")])
    mensagem = TextAreaField('Detalhes do Problema ou Dúvida', validators=[input_required(message="A mensagem não pode ficar vazia.")])


class AdicionarSaldoForm(FlaskForm):
    valor = FloatField('Valor do Depósito (R$)', validators=[
        input_required(message="Digite um valor para depositar."),
        NumberRange(min=0.01, message="O valor tem que ser maior que 0"),
    ])


class FormularioEntregaForm(FlaskForm):
    arquivo_entrega = FileField('Arquivo da entrega', validators=[
        input_required(message="Envie o arquivo .zip da entrega."),
        FileAllowed(['zip'], 'Apenas arquivos .zip são permitidos.')
    ])


class AvaliacaoForm(FlaskForm):
    nota = IntegerField('Nota', validators=[input_required(message="Escolha uma nota de 1 a 5.")])
    comentario = TextAreaField('Comentário', validators=[input_required(message="Deixe uma descrição.")])

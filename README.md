# 99Dev

Plataforma web que conecta clientes a desenvolvedores freelancers. O cliente publica uma demanda técnica e o dev pode visualizá-la e registrar tarefas. O projeto é o trabalho interdisciplinar do 1º período do curso de Bacharelado em Engenharia de Software do IFPB — Campus João Pessoa, integrando as disciplinas de Programação Web I, Introdução à Programação e Introdução à Engenharia de Software.

---

## Integrantes

| Nome 
|------|
| Lucas Francelino de Pontes
| Theo Nogueira Virginio
| João Tigre
| Felipe Flor 

---

## Tecnologias utilizadas

- Python 3.13
- Flask + Flask-WTF + Flask-Mail
- SQLAlchemy (SQLite)
- Authlib (login social via Google OAuth)
- Jinja2 (templates com herança)
- HTML5 + CSS3
- CSV (persistência de demandas)
- bcrypt (hash de senhas)
- itsdangerous (tokens de recuperação de senha)
- python-dotenv (variáveis de ambiente)
- Git e GitHub

---

## Funcionalidades implementadas

**Visitante**
- Visualizar página inicial
- Criar conta (cliente ou dev)
- Login tradicional ou via Google (OAuth)
- Recuperar senha por e-mail (token com expiração)

**Cliente**
- Gerenciar perfil (e-mail, senha, foto, descrição)
- Publicar demandas (título, tecnologia, descrição, orçamento)
- Visualizar histórico de demandas com filtro por status (Aberta / Pendente / Fechada)
- Buscar demandas por texto
- Visualizar e responder candidaturas de devs
- Aprovar ou recusar entregas
- Gerenciar saldo e histórico de pagamentos
- Avaliar desenvolvedores após conclusão do serviço
- Conversar com o dev via chat em tempo real
- Enviar mensagens de suporte

**Desenvolvedor**
- Gerenciar perfil dev (nome, título, skills, valor/hora, GitHub, LinkedIn, resumo, foto e banner)
- Visualizar demandas disponíveis
- Candidatar-se a demandas com proposta
- Acompanhar projetos e candidaturas em andamento
- Visualizar saldo
- Conversar com o cliente via chat em tempo real
- Enviar mensagens de suporte

---
## Estrutura do projeto

```
99dev/
├── main.py                    # Rotas e formulários Flask
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py            # Configuração da app (Flask, Mail, DB, OAuth)
│   ├── models.py               # Models: Cliente, Desenvolvedor, Pagamento, Candidatura, MensagemChat
│   ├── functions.py            # Lógica de negócio (cadastro, autenticação, CSV, chat, pagamentos...)
│   └── decorators.py           # login_required
├── templates/
│   ├── home.html
│   ├── header.html
│   ├── baseAutenticacao.html   # Template base — telas de autenticação
│   ├── basePerfil.html         # Template base — área logada
│   ├── cadastro.html
│   ├── login.html
│   ├── recuperar-senha.html
│   ├── nova-senha.html
│   ├── perfil.html             # Perfil do dev
│   ├── perfil-editar.html      # Edição de perfil
│   ├── dashboardCliente.html
│   ├── dashboardDev.html
│   ├── MeusProjetos.html
│   ├── Meusprojetosdev.html
│   ├── carteiraCliente.html
│   ├── chat.html
│   ├── suporte.html
│   ├── suporteDev.html
│   └── 403.html
├── static/
│   ├── css/
│   ├── img/
│   └── uploads/perfil/         # Fotos de perfil (geradas em runtime)
└── data/
    └── demandas.csv            # Persistência das demandas
```

## Como executar o projeto

### Pré-requisitos

- Python 3.10 ou superior
- pip

### Passo a passo

**1. Clone o repositório**

```bash
git clone https://github.com/<seu-usuario>/99dev.git
cd 99dev
```

**2. Crie e ative o ambiente virtual**

```bash
# Criar
python -m venv venv

# Ativar — Linux/macOS
source venv/bin/activate

# Ativar — Windows (PowerShell)
venv\Scripts\activate

# Ativar — Windows (Git Bash)
source venv/Scripts/activate
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Execute a aplicação**

```bash
python main.py
```

**5. Acesse no navegador**

```
http://127.0.0.1:3001
```

---

## Arquitetura do sistema

![Diagrama de Uso](https://docs.google.com/uc?export=view&id=1XFoq7EcP9YiZdQ1O8kK-SscItWtWL2eH)

---

## Diagrama de Casos de Uso

![Diagrama de Uso](https://docs.google.com/uc?export=view&id=1L_T9k_HK8a0hrnt16eX9-132T97NPO7T)

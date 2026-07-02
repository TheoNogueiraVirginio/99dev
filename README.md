# 99Dev

Plataforma web que conecta clientes a desenvolvedores freelancers. O cliente publica uma demanda técnica, devs se candidatam com uma proposta, conversam em chat, entregam o projeto e recebem pagamento via carteira interna. O projeto é o trabalho interdisciplinar do 1º período do curso de Bacharelado em Engenharia de Software do IFPB — Campus João Pessoa, integrando as disciplinas de Programação Web I, Introdução à Programação e Introdução à Engenharia de Software.

---

## Integrantes

| Nomes |
|------|
| Lucas Francelino de Pontes |
| Theo Nogueira Virginio |
| João Tigre |
| Felipe Flor |

---

## Tecnologias utilizadas

- **Python 3.13**
- **Flask** — framework web
- **Flask-WTF** — formulários e proteção CSRF
- **Flask-SQLAlchemy** (SQLite) — ORM e persistência de usuários, candidaturas, entregas, pagamentos e chat
- **Flask-Mail** — envio de e-mails (recuperação de senha)
- **Authlib** — login social via Google OAuth
- **bcrypt** — hash de senhas
- **itsdangerous** — geração/validação de tokens de recuperação de senha
- **python-dotenv** — variáveis de ambiente
- **email-validator** — validação de e-mail nos formulários
- **requests** — chamadas HTTP auxiliares
- **CSV** — persistência de demandas, tickets de suporte e avaliações
- **Jinja2** — templates com herança
- **HTML5 + CSS3**
- **Git e GitHub**

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
- Visualizar histórico de demandas com filtro por status e busca por texto
- Visualizar e aceitar candidaturas de devs
- Conversar com o dev via chat (long-polling)
- Aprovar ou recusar entregas
- Baixar o arquivo entregue pelo dev
- Pagar a demanda concluída (débito da carteira do cliente e crédito na do dev)
- Gerenciar saldo e histórico de pagamentos
- Avaliar o desenvolvedor após a conclusão do serviço
- Enviar mensagens de suporte

**Desenvolvedor**
- Gerenciar perfil (nome, título, skills, valor/hora, GitHub, LinkedIn, resumo, foto e banner)
- Visualizar demandas disponíveis
- Candidatar-se a demandas com proposta
- Conversar com o cliente via chat (long-polling)
- Acompanhar projetos e candidaturas em andamento
- Enviar a entrega do projeto (upload de arquivo .zip)
- Visualizar saldo e histórico de pagamentos recebidos
- Enviar mensagens de suporte (canal específico para devs)

---

## Estrutura do projeto

```
99dev/
├── main.py                          # Ponto de entrada — sobe a aplicação Flask
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── __init__.py                  # Cria a app Flask, DB, Mail, OAuth e registra os blueprints
│   ├── models.py                    # Models: Cliente, Desenvolvedor, Pagamento, Entrega, Candidatura, MensagemChat
│   ├── functions.py                 # Regras de negócio (cadastro, autenticação, demandas, chat, pagamentos, entregas...)
│   ├── forms.py                     # Formulários WTForms centralizados
│   ├── decorators.py                # login_required
│   └── blueprints/                  # Rotas organizadas por domínio
│       ├── auth/                    # Cadastro, login, login Google, recuperação de senha, logout
│       ├── perfil/                  # Edição de perfil (cliente e dev)
│       ├── cliente/                 # Dashboard, demandas, carteira, pagamento, aprovação/recusa de entrega, avaliação
│       ├── dev/                     # Dashboard, carteira, projetos, envio de entrega
│       ├── entregas/                # Download do arquivo entregue
│       ├── candidatura/             # Candidatar-se a demanda, aceitar candidatura
│       ├── chat/                    # Conversa entre cliente e dev (envio/leitura de mensagens)
│       └── suporte/                 # Contato com a equipe de suporte (cliente e dev)
├── templates/
│   ├── home.html
│   ├── header.html
│   ├── baseAutenticacao.html        # Template base — telas de autenticação
│   ├── basePerfil.html              # Template base — área logada
│   ├── cadastro.html
│   ├── login.html
│   ├── recuperar-senha.html
│   ├── nova-senha.html
│   ├── perfil.html                  # Perfil do dev
│   ├── perfil-editar.html           # Edição de perfil do cliente
│   ├── dashboardCliente.html
│   ├── dashboardDev.html
│   ├── MeusProjetos.html
│   ├── Meusprojetosdev.html
│   ├── carteiraCliente.html
│   ├── carteiraDev.html
│   ├── chat.html
│   ├── suporte.html
│   ├── suporteDev.html
│   └── 403.html
├── static/
│   ├── css/
│   ├── img/
│   └── uploads/                     # Fotos de perfil/banner e entregas (geradas em runtime)
└── data/
    ├── 99dev.db                     # Banco SQLite (usuários, candidaturas, entregas, pagamentos, chat)
    ├── demandas.csv                 # Persistência das demandas
    ├── suporte.csv / suporte_dev.csv# Tickets de suporte
    └── avaliacoes.csv               # Avaliações registradas pelos clientes
```

> A pasta `data/` precisa existir na raiz do projeto antes da primeira execução — é onde o SQLite cria `99dev.db` e onde os CSVs de demandas, suporte e avaliações são gravados.

---

## Como baixar e executar o projeto

### Pré-requisitos

- Python 3.10 ou superior
- pip
- Conta de e-mail com senha de aplicativo (Gmail), se for testar o envio de e-mails
- Credenciais OAuth do Google, se for testar o login social

### Passo a passo

**1. Clone o repositório**

```bash
git clone https://github.com/TheoNogueiraVirginio/99dev.git
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

**4. Configure as variáveis de ambiente**

Copie o arquivo de exemplo e preencha com seus valores:

```bash
cp .env.example .env
```

```
SECRET_KEY="chave_secreta_flask"
GOOGLE_CLIENT_ID="id_do_google_oauth"
GOOGLE_CLIENT_SECRET="secret_do_google_oauth"
MAIL_PASSWORD="senha_de_aplicativo_do_gmail"
```

**5. Crie a pasta de dados**

```bash
mkdir data
```

**6. Execute a aplicação**

```bash
python main.py
```

**7. Acesse no navegador**

```
http://127.0.0.1:3001
```

---

## Arquitetura do sistema

![Diagrama de Arquitetura](https://docs.google.com/uc?export=view&id=1nugxd1U1P3jEk9QzrtG9JM6WPJAqSyoK)

---

## Diagrama de Casos de Uso

![Diagrama de Casos de Uso](https://docs.google.com/uc?export=view&id=1QvalDWfEoOhiOklEoJJBfu1PfX3C28_H)
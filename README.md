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
- Jinja2 (templates)
- HTML5 + CSS3
- CSV (persistência de demandas)
- bcrypt (hash de senhas)
- Git e GitHub

---

## Funcionalidades implementadas

**Visitante**
- Visualizar página inicial
- Criar conta (cliente ou dev)

**Cliente**
- Gerenciar perfil (e-mail, senha, foto, descrição)
- Publicar demandas (título, tecnologia, descrição, orçamento)
- Visualizar histórico de demandas com filtro por status (Aberta / Pendente / Fechada)
- Buscar demandas por texto

**Desenvolvedor**
- Gerenciar perfil dev (nome, título, skills, valor/hora, GitHub, LinkedIn, resumo)
- Visualizar demandas disponíveis

---

## Estrutura do projeto

```
99dev/
├── main.py                  # Rotas e formulários Flask
├── requirements.txt
├── .gitignore
├── app/
│   ├── __init__.py          # Configuração da app (Flask, Mail, DB)
│   ├── models.py            # Models: Usuario, PerfilDev
│   ├── functions.py         # Lógica de negócio (cadastro, autenticação, CSV...)
│   └── decorators.py        # login_required
├── templates/
│   ├── home.html
│   ├── cadastro.html
│   ├── login.html
│   ├── recuperar-senha.html
│   ├── nova-senha.html
│   ├── perfil.html          # Perfil do dev
│   ├── perfil-editar.html   # Edição de perfil do cliente
│   ├── dashboardCliente.html
│   ├── MeusProjetos.html
│   └── 403.html
├── static/
│   ├── css/
│   ├── img/
│   └── uploads/perfil/      # Fotos de perfil (geradas em runtime)
└── data/
    └── demandas.csv         # Persistência das demandas
```

---

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

```
Sprint 2
```

---

## Diagrama de Casos de Uso

![Diagrama de Uso](https://docs.google.com/uc?export=view&id=1L_T9k_HK8a0hrnt16eX9-132T97NPO7T)